"""The classifier registry, and the title collisions it exists to prevent.

A document's identity is its title: the backend upserts on
``(entity_id, context_type, title)``, so two examples that render one title do
not conflict -- the second overwrites the first and the example is lost with no
signal. ``_CAPABILITY_LABEL`` was added after exactly that happened to an omni
model, which shipped one of its three capabilities' examples and silently
dropped the other two.

These tests hold the line in three places: every value an example uses is
registered, no raw value can reach a customer-facing title, and no two examples
that can be selected for the SAME service render the same title.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from unitysvc_data import classifiers

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_build_module():
    """Import ``tools/build.py`` as a module without adding tools/ to sys.path."""
    path = REPO_ROOT / "tools" / "build.py"
    spec = importlib.util.spec_from_file_location("unitysvc_data_build_for_classifiers", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build = _load_build_module()
from unitysvc_data.presets import (
    _PRESET_APPLIES_TO,
    MANIFEST,
    _title,
)


def _llm_presets() -> dict[str, dict]:
    """One entry per preset_name (not per version) for the llm family."""
    out: dict[str, dict] = {}
    for key, entry in MANIFEST["presets"].items():
        if key.startswith("llm_"):
            out.setdefault(entry.get("preset_name", key), entry)
    return out


# --------------------------------------------------------------------------- #
# The registry covers the corpus
# --------------------------------------------------------------------------- #
def test_every_value_in_use_is_registered():
    """An unregistered value would reach ``_title`` as a raw token.

    ``tools/build.py`` rejects one at authoring time; this is the corpus-wide
    statement of the same rule, so it also covers values introduced by a
    manifest edited by hand.
    """
    problems = []
    for name, spec in sorted(_PRESET_APPLIES_TO.items()):
        for message in classifiers.validate(spec):
            problems.append(f"{name}: {message}")

    assert not problems, "unregistered applies_to values:\n" + "\n".join(problems)


#: The qualifier bits ``_title`` may add that are NOT classifier labels: the
#: client library, read from ``meta.requirements`` to tell an SDK example from a
#: raw-HTTP one in the same language.
_SDK_BITS = frozenset({"requests", "openai SDK", "anthropic SDK", "cohere SDK", "boto3 SDK"})


def _allowed_bits() -> set[str]:
    """Every string a title's parenthesised list may legally contain."""
    allowed = set(_SDK_BITS)
    for axis_name, axis in classifiers.AXES.items():
        for entry in axis.values.values():
            if not entry.label:
                continue
            allowed.add(entry.label)
            if axis_name == "dialect" and entry.caller_dialect:
                allowed.add(f"{entry.label} input")
    return allowed


def test_no_raw_value_reaches_a_title():
    """Every qualifier in a title is a declared label, never a bare value.

    ``dashscope_audio_task`` had no label, so ``_title`` fell through to
    ``.get(dialect, dialect)`` and eight shipped titles read
    ``(speech, dashscope_audio_task)``. Checking the bits -- rather than
    searching the title for the value -- is what makes this precise: ``embed``
    is a substring of its own label ``embeddings``, and ``openai`` appears
    legitimately in the ``openai SDK`` bit.
    """
    allowed = _allowed_bits()
    leaks = []
    for name, entry in sorted(MANIFEST["presets"].items()):
        spec = _PRESET_APPLIES_TO.get(entry.get("preset_name", name)) or {}
        title = _title(entry, spec)
        if "(" not in title:
            continue
        for bit in title[title.index("(") + 1 : title.rindex(")")].split(", "):
            if bit not in allowed:
                leaks.append(f"{name}: undeclared qualifier {bit!r} in {title!r}")

    assert not leaks, "titles carrying something that is not a declared label:\n" + "\n".join(leaks)


# --------------------------------------------------------------------------- #
# Titles stay distinct for everything one service can be served
# --------------------------------------------------------------------------- #
def test_the_corpus_has_no_reachable_title_clash():
    """Drives the real guard in ``tools/build.py`` rather than a copy of it.

    The co-occurrence rule lives in the registry (``Axis.co_occurs``) and the
    comparison lives in ``build.check_titles``; duplicating either here would
    let the test and the build disagree about what a clash is.
    """
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors, errors.messages

    build.check_titles(presets, errors)

    assert not errors.messages, "reachable title clashes:\n" + "\n".join(errors.messages)


def test_the_registry_itself_is_sound():
    """Stated over the DECLARED values, so it covers ones no example uses yet."""
    assert classifiers.check_registry() == []


def test_an_unlabelled_value_on_a_co_occurring_axis_is_caught(monkeypatch):
    """Proof the registry check can fail.

    An axis whose values render nothing cannot keep two documents apart.
    """
    monkeypatch.setitem(classifiers.DIALECTS, "newsurface", classifiers.Classifier(""))

    problems = classifiers.check_registry()

    assert len(problems) == 1
    assert "no display label" in problems[0]


def test_an_undeclared_shared_label_is_caught(monkeypatch):
    """Two values rendering one string must be declared in SHARED_LABELS."""
    monkeypatch.setitem(
        classifiers.DIALECTS, "newsurface", classifiers.Classifier("Cohere SDK")
    )

    problems = classifiers.check_registry()

    assert len(problems) == 1
    assert "share the display label" in problems[0]


def test_an_unlabelled_value_on_an_exclusive_axis_is_fine():
    """``upstream`` values are all unlabelled on purpose.

    One collection is built with one upstream, so two examples declaring
    different ones never meet and their titles may coincide. The check must not
    demand labels it would then have to render on ~80% of titles.
    """
    assert not classifiers.co_occurs("upstream")
    assert all(not entry.label for entry in classifiers.UPSTREAMS.values())
    assert classifiers.check_registry() == []


def test_a_merged_dashscope_label_is_caught_by_the_build(monkeypatch):
    """Proof the corpus guard can fail, against the clash that motivated it."""
    monkeypatch.setitem(
        classifiers.DIALECTS,
        "dashscope_text",
        classifiers.Classifier("DashScope", caller_dialect=True),
    )

    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    build.check_titles(presets, errors)

    assert any("would overwrite the other" in m for m in errors.messages), errors.messages


def test_the_dashscope_surfaces_stay_distinguishable():
    """The specific pair that motivated the registry.

    Chat is served at ``text-generation`` on a text model and at
    ``multimodal-generation`` on an omni one; text-to-speech is reachable on
    both the audio-task surface and the omni one. All four tokens shared the
    label ``"DashScope"``, so their titles were identical.
    """
    labels = {
        value: classifiers.label("dialect", value)
        for value in ("dashscope", "dashscope_text", "dashscope_multimodal", "dashscope_audio_task")
    }

    assert labels["dashscope_text"] != labels["dashscope_multimodal"]
    assert labels["dashscope_audio_task"] != labels["dashscope_multimodal"]
    assert all(labels.values()), f"an unlabelled DashScope surface leaks its token: {labels}"


def test_a_raw_value_fallback_is_caught(monkeypatch):
    """Proof the leak guard above can fail.

    ``_title`` used to read ``_DIALECT_LABEL.get(dialect, dialect)``, falling
    back to the raw token for an unregistered value. ``classifiers.label``
    returns ``""`` instead, so the leak is structurally impossible -- this
    asserts the guard would notice if that fallback came back.
    """
    monkeypatch.setattr(
        classifiers, "label", lambda axis, value: value or "", raising=True
    )

    with pytest.raises(AssertionError, match="not a declared label"):
        test_no_raw_value_reaches_a_title()


def test_an_unknown_value_is_rejected_with_a_hint():
    problems = classifiers.validate({"dialect": "opena"})

    assert len(problems) == 1
    assert "'openai'" in problems[0]


def test_a_valid_block_has_no_problems():
    assert classifiers.validate({"capability": "text-to-speech", "dialect": "openai"}) == []


def test_an_empty_block_is_valid():
    """No constraints means "applies to every service" -- how ``llm_description``
    is expressed, not an error."""
    assert classifiers.validate({}) == []


def test_a_non_string_value_is_rejected():
    assert classifiers.validate({"capability": ["chat"]}) == [
        "applies_to.capability must be a string, got list"
    ]


# --------------------------------------------------------------------------- #
# A document that has no feature bit of its own: the request template
# --------------------------------------------------------------------------- #
#
# ``chat`` and ``image-text-to-text`` are both unlabelled. The registry's
# argument for why that is safe used to be about EXAMPLES: every image-text-to-
# text example declares ``feature = "vision"``, so its title always carries the
# qualifier and the pair never renders alike. A request template declares no
# feature, so that argument does not reach it -- a service with both capabilities
# would be handed two documents titled "Default request body", and the second
# would silently replace the first. The title builder now renders the qualifier
# a capability is *carried by* whether or not the document declares it, so the
# argument no longer depends on what any one document says.
def _request_template_title(capability: str) -> str:
    """The title a request template for ``capability`` renders.

    Built from the capability alone, because that is all a request template
    declares: it bundles every request format, so it has no dialect, and it has
    no feature.
    """
    return _title({"category": "request_template", "mime_type": "json"}, {"capability": capability})


def test_no_two_capabilities_render_one_request_template_title():
    """Stated over every REGISTERED capability, not the ones that happen to have a
    template yet, so it holds for a capability added later.

    Every capability can meet every other on one service -- a collection fans out
    over the whole list the offering declares -- so any two that render the same
    title would overwrite one another in the ``documents`` mapping.
    """
    by_title: dict[str, list[str]] = {}
    for capability in classifiers.CAPABILITIES:
        by_title.setdefault(_request_template_title(capability), []).append(capability)

    clashes = {title: caps for title, caps in by_title.items() if len(caps) > 1}
    assert not clashes, f"request templates for these capabilities share a title: {clashes}"


def test_the_chat_request_template_keeps_the_title_it_was_published_under():
    """A title is a document's key: the backend upserts on
    ``(entity_id, context_type, title)``. Renaming chat's would orphan the
    existing document on every published service and mint a new one -- and
    hand-written listings key their own "Default request body" entry to it.
    Telling the capabilities apart must therefore happen on the OTHER side.
    """
    assert _request_template_title("chat") == "Default request body"


def test_image_text_to_text_is_told_apart_by_the_feature_that_carries_it():
    """Vision is the qualifier the registry has always said names this
    capability; the template reads it the way the examples do."""
    assert classifiers.carried_by("capability", "image-text-to-text") == "vision"
    assert _request_template_title("image-text-to-text") == "Default request body (vision)"


def test_a_carried_feature_is_not_repeated_when_the_document_declares_it():
    """Every image-text-to-text EXAMPLE already declares ``feature = "vision"``.
    Their titles must come out byte-identical, not "(vision, vision)" -- a title
    is a key, so a changed one is a different document."""
    declared = _title(
        {"category": "code_example", "mime_type": "python", "meta": {"requirements": ["requests"]}},
        {"capability": "image-text-to-text", "dialect": "openai", "feature": "vision"},
    )
    assert declared == "Python code example (vision, requests)"


def test_a_capability_carries_no_feature_unless_the_registry_says_so():
    """Only image-text-to-text is carried; naming a feature on any other capability
    would add a qualifier to titles that are already published."""
    carried = {c for c in classifiers.CAPABILITIES if classifiers.carried_by("capability", c)}
    assert carried == {"image-text-to-text"}


def test_a_carrier_that_renders_nothing_is_caught(monkeypatch):
    """A capability carried by a feature that has no label is still bare."""
    monkeypatch.setitem(
        classifiers.CAPABILITIES,
        "image-text-to-text",
        classifiers.Classifier("", carried_by="telepathy"),
    )

    problems = classifiers.check_registry()

    assert any("carried_by" in p and "telepathy" in p for p in problems), problems


def test_a_carrier_on_a_labelled_value_is_caught(monkeypatch):
    """``carried_by`` stands in for a label the value lacks. On one that has a
    label it would only append a second qualifier to every title."""
    monkeypatch.setitem(
        classifiers.CAPABILITIES, "embed", classifiers.Classifier("embeddings", carried_by="vision")
    )

    problems = classifiers.check_registry()

    assert any("embed" in p and "both the label" in p for p in problems), problems


def test_two_bare_capabilities_are_caught(monkeypatch):
    """Proof the registry check can fail, against the very pair this exists for.

    Without a carrier ``image-text-to-text`` is as bare as ``chat``, and nothing
    but a document happening to declare ``feature = "vision"`` would keep their
    titles apart -- which is exactly the reasoning that failed for templates.
    """
    monkeypatch.setitem(
        classifiers.CAPABILITIES, "image-text-to-text", classifiers.Classifier("")
    )

    problems = classifiers.check_registry()

    assert any("chat" in p and "image-text-to-text" in p and "bare" in p for p in problems), problems


def test_the_request_template_pin_fails_without_the_carrier(monkeypatch):
    """Proof the pin above can fail: it is the test that fails on the title
    builder as it was before ``carried_by`` existed."""
    monkeypatch.setitem(
        classifiers.CAPABILITIES, "image-text-to-text", classifiers.Classifier("")
    )

    with pytest.raises(AssertionError, match="share a title"):
        test_no_two_capabilities_render_one_request_template_title()
