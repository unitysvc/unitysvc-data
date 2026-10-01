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
