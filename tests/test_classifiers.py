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

import itertools

import pytest

from unitysvc_data import classifiers
from unitysvc_data.presets import (
    _PRESET_APPLIES_TO,
    MANIFEST,
    _applies,
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
    for axis, values in classifiers.AXES.items():
        for entry in values.values():
            if not entry.label:
                continue
            allowed.add(entry.label)
            if axis == "dialect" and entry.caller_dialect:
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
def _co_selectable(spec_a: dict, spec_b: dict) -> bool:
    """Whether one service's collection can contain both examples.

    Mirrors how ``llm_example_collection`` queries: ``capability`` is fanned
    (each iteration adds to the same ``documents`` mapping, so two capabilities
    DO meet there), ``dialect`` and ``feature`` are matched against SETS, and
    ``upstream`` is a single value for the whole collection
    (``source["upstream_dialect"]``) -- which is the one axis that makes two
    presets mutually exclusive.
    """
    up_a, up_b = spec_a.get("upstream"), spec_b.get("upstream")
    if up_a is not None and up_b is not None and up_a != up_b:
        return False

    context = {
        "dialects": {spec_a.get("dialect"), spec_b.get("dialect")} - {None},
        "upstream": up_a or up_b or "openai",
        "features": {spec_a.get("feature"), spec_b.get("feature")} - {None} or {"streaming"},
    }
    return all(
        _applies(spec, capability=spec.get("capability") or "chat", **context)
        for spec in (spec_a, spec_b)
    )


def test_co_selectable_examples_have_distinct_titles():
    """The collision that loses an example, stated over the whole corpus.

    Two presets that differ only on an axis whose label is empty render one
    title. Adding an axis with no label, or giving two values the same label,
    fails here.
    """
    presets = _llm_presets()
    specs = {n: _PRESET_APPLIES_TO.get(n) or {} for n in presets}
    titles = {n: _title(presets[n], specs[n]) for n in presets}

    collisions = []
    for a, b in itertools.combinations(sorted(presets), 2):
        if titles[a] != titles[b] or specs[a] == specs[b]:
            continue  # distinct, or version siblings sharing a title correctly
        if _co_selectable(specs[a], specs[b]):
            differ = sorted(k for k in set(specs[a]) | set(specs[b]) if specs[a].get(k) != specs[b].get(k))
            collisions.append(f"{titles[a]!r}: {a} vs {b} (differ on {differ})")

    assert not collisions, (
        "these examples can land on one service and would overwrite each other:\n"
        + "\n".join(collisions)
    )


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


def test_a_shared_label_is_caught(monkeypatch):
    """Proof the collision test above can fail.

    A fitness function that cannot fail is worthless, so merge two labels and
    assert the corpus check notices.
    """
    monkeypatch.setitem(
        classifiers.DIALECTS,
        "dashscope_text",
        classifiers.Classifier("DashScope", caller_dialect=True),
    )

    with pytest.raises(AssertionError, match="overwrite each other"):
        test_co_selectable_examples_have_distinct_titles()


# --------------------------------------------------------------------------- #
# validate()
# --------------------------------------------------------------------------- #
def test_an_unknown_key_is_rejected_with_a_hint():
    """A misspelled axis WIDENS the selector, so it must not pass silently."""
    problems = classifiers.validate({"capabilty": "chat"})

    assert len(problems) == 1
    assert "not a constraint" in problems[0]
    assert "'capability'" in problems[0]


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
