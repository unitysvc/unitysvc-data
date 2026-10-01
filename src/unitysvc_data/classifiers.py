"""The classifier registry — the values ``applies_to`` may use, and how each reads.

``applies_to`` decides which examples a service gets (see ``tools/build.py``).
Its four axes used to be documented only in a comment and validated nowhere, so
a typo silently *widened* a selector rather than narrowing it: an absent key
means "no constraint", so ``capabilty = "chat"`` made an example apply to every
service. One such omission had to be found by hand and fixed in 0.2.3
(``llm/code-example-tts-shell``, which named a capability but no dialect).

This module is the single declaration of what each axis denotes and which values
it accepts. ``tools/build.py`` rejects anything else, with a near-miss hint.

It also carries each value's **display label**, which is what ``presets._title``
renders. Keeping the labels here rather than in private tables next to the title
builder buys two things:

* a value cannot be used without being registered, so no raw token can reach a
  customer-facing title (``dashscope_audio_task`` did exactly that: eight titles
  read ``(speech, dashscope_audio_task)``);
* an empty label becomes declared data rather than a hardcoded skip, so "why is
  ``openai`` invisible in titles?" is answered next to the value.

A title is a document's KEY -- the backend upserts on
``(entity_id, context_type, title)``. Two values that share a label therefore
merge two documents into one, and the loser is silently overwritten. That is why
labels must stay distinct wherever the values they name can appear on one
service, and why ``tests/test_classifiers.py`` asserts it against the real
selector rather than trusting this docstring.
"""

from __future__ import annotations

import difflib
from typing import NamedTuple


class Classifier(NamedTuple):
    """One allowed value of one axis."""

    #: How the value reads inside a title's parenthesised qualifier list.
    #: Empty means "contributes nothing" -- a deliberate choice, explained in
    #: ``note``, not an oversight.
    label: str
    #: Rendered as ``"<label> input"``: the label names a request *dialect* the
    #: caller writes, not a client library. ``cohere`` is a named SDK and reads
    #: as itself; ``anthropic`` is a wire shape and reads as "Anthropic-style
    #: input".
    caller_dialect: bool = False
    #: Why the label is empty, or anything else a reader needs. Documentation
    #: only; nothing reads it.
    note: str = ""


# --------------------------------------------------------------------------- #
# capability -- what the example demonstrates. The offering declares a LIST of
# these, and a collection fans out over every one, so two presets with
# different capabilities both land in one ``documents`` mapping. Their titles
# must differ: an omni model declaring chat, text-to-speech and speech-to-text
# used to ship ONE of those three sets, the other two overwritten by title.
# --------------------------------------------------------------------------- #
CAPABILITIES: dict[str, Classifier] = {
    "chat": Classifier("", note="A bare title already reads as chat; labelling it would churn nearly every published service for no gain."),
    "image-text-to-text": Classifier("", note="Carried by the `vision` feature bit instead, so it cannot collide with a labelled sibling."),
    "embed": Classifier("embeddings"),
    "rerank": Classifier("rerank"),
    "moderate": Classifier("moderation"),
    "image-generate": Classifier("image"),
    "image-edit": Classifier("image edit"),
    "video-generate": Classifier("video"),
    "speech-to-text": Classifier("transcription"),
    "text-to-speech": Classifier("speech"),
}

# --------------------------------------------------------------------------- #
# dialect -- the request shape the CALLER writes. A service's `input_formats` is
# a SET, so two presets with different dialects can both be selected for one
# service; their labels must therefore stay distinct.
#
# The DashScope tokens are finer than the `dashscope` request format, because
# they name different native endpoints and body shapes: text-generation,
# multimodal-generation, and the audio-task surface. A model serves one of them,
# so a service does not normally declare two -- but `text` and `multimodal`
# shared the label "DashScope" and so rendered identical titles, which is a
# silent overwrite waiting for the first service that does.
# --------------------------------------------------------------------------- #
DIALECTS: dict[str, Classifier] = {
    "openai": Classifier("", note="The platform's default dialect: naming it in every title would say nothing."),
    "anthropic": Classifier("Anthropic-style", caller_dialect=True),
    "cohere": Classifier("Cohere SDK"),
    "cerebras": Classifier("Cerebras SDK"),
    "bedrock_converse": Classifier("boto3 Converse"),
    "bedrock_invoke": Classifier("boto3 InvokeModel"),
    "huggingface": Classifier("sentence-transformers"),
    "dashscope": Classifier("DashScope", caller_dialect=True),
    "dashscope_text": Classifier("DashScope text", caller_dialect=True),
    "dashscope_multimodal": Classifier("DashScope", caller_dialect=True),
    "dashscope_audio_task": Classifier("DashScope audio task"),
}

# --------------------------------------------------------------------------- #
# upstream -- the dialect the service's upstream speaks, which differs from
# `dialect` when the gateway translates.
#
# Every label here is empty, and unlike the other axes that is not a style
# choice: a collection is built with exactly ONE upstream
# (`source["upstream_dialect"]`), so two presets that declare different
# upstreams can never be selected together and cannot collide however they are
# titled. Giving the axis a label would add "via OpenAI" to ~80% of titles to
# separate documents that are already separate.
# --------------------------------------------------------------------------- #
UPSTREAMS: dict[str, Classifier] = {
    "openai": Classifier("", note="One upstream per collection, so this axis cannot cause a title collision."),
    "anthropic": Classifier("", note="See `openai`."),
    "dashscope": Classifier("", note="See `openai`."),
}

# --------------------------------------------------------------------------- #
# feature -- an attribute the service must advertise before the example applies.
# Passed as a SET, so these can co-occur and must stay distinct.
# --------------------------------------------------------------------------- #
FEATURES: dict[str, Classifier] = {
    "streaming": Classifier("streaming"),
    "tools": Classifier("tools"),
    "vision": Classifier("vision"),
}

#: Axis name -> its allowed values. The keys are exactly the keys
#: ``applies_to`` accepts.
AXES: dict[str, dict[str, Classifier]] = {
    "capability": CAPABILITIES,
    "dialect": DIALECTS,
    "upstream": UPSTREAMS,
    "feature": FEATURES,
}


def classifier(axis: str, value: str) -> Classifier:
    """The registry entry for one value.

    Raises:
        KeyError: The axis or the value is not registered. Callers that reach
            here have skipped :func:`validate`, which is the layer meant to
            produce a readable message.
    """
    return AXES[axis][value]


def label(axis: str, value: str | None) -> str:
    """How a value reads in a title, or ``""`` when it contributes nothing.

    An unregistered value returns ``""`` rather than raising, so a title is
    never built out of a raw token. Validation is what rejects it; this only
    refuses to leak it.
    """
    if value is None:
        return ""
    entry = AXES.get(axis, {}).get(value)
    return entry.label if entry else ""


def is_caller_dialect(value: str | None) -> bool:
    """Whether a dialect's label names a wire shape rather than a client."""
    entry = DIALECTS.get(value or "")
    return bool(entry and entry.caller_dialect)


def validate(applies_to: dict[str, object]) -> list[str]:
    """Every problem with one ``applies_to`` block, as readable messages.

    Returns an empty list when the block is valid. Unknown keys are reported
    as well as unknown values, because an absent key means "no constraint": a
    misspelled axis does not narrow the selector, it silently widens it.
    """
    problems: list[str] = []
    for axis, value in sorted(applies_to.items()):
        allowed = AXES.get(axis)
        if allowed is None:
            hint = difflib.get_close_matches(axis, AXES, n=1)
            suffix = f" Did you mean {hint[0]!r}?" if hint else ""
            problems.append(
                f"unknown applies_to key {axis!r} -- an unrecognised key is not a "
                f"constraint, so the example would apply to every service.{suffix}"
            )
            continue
        if not isinstance(value, str):
            problems.append(f"applies_to.{axis} must be a string, got {type(value).__name__}")
            continue
        if value not in allowed:
            hint = difflib.get_close_matches(value, allowed, n=1)
            suffix = f" Did you mean {hint[0]!r}?" if hint else ""
            problems.append(
                f"unknown {axis} {value!r}. Register it in "
                f"src/unitysvc_data/classifiers.py (with the label it should "
                f"read as in a title) or fix the spelling.{suffix}"
            )
    return problems
