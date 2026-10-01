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
    # Named for the surface, not for one model family: the same
    # ``/models/<model>`` inference API serves sentence embeddings, image
    # editing and text-to-video. It was "sentence-transformers", which could
    # not honestly title the image-edit and video examples that also speak it.
    "huggingface": Classifier("Hugging Face"),
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

class Axis(NamedTuple):
    """One ``applies_to`` key: its allowed values, and how it behaves."""

    values: dict[str, Classifier]
    #: Whether two examples differing ONLY on this axis can both end up in one
    #: service's ``documents`` mapping. When they can, their titles MUST differ
    #: or one silently overwrites the other -- which makes this flag the input
    #: to the collision check, not documentation.
    co_occurs: bool
    note: str = ""


#: Axis name -> the axis. The keys are exactly the keys ``applies_to`` accepts.
AXES: dict[str, Axis] = {
    "capability": Axis(
        CAPABILITIES,
        co_occurs=True,
        note="A collection fans out over every capability the offering declares, "
        "and each iteration adds to the SAME documents mapping, so two "
        "capabilities meet there.",
    ),
    "dialect": Axis(
        DIALECTS,
        co_occurs=True,
        note="`input_formats` is a set, so one service can be served examples "
        "for several dialects at once.",
    ),
    "upstream": Axis(
        UPSTREAMS,
        co_occurs=False,
        note="A collection is built with exactly ONE upstream "
        "(`source['upstream_dialect']`), so two examples declaring different "
        "upstreams are never selected together and cannot collide however "
        "they are titled. This is why every upstream label is empty.",
    ),
    "feature": Axis(
        FEATURES,
        co_occurs=True,
        note="Matched against a set, so a streaming example and a tools "
        "example can both apply.",
    ),
}

#: ``(axis, value)`` pairs whose empty label is deliberate, on an axis whose
#: values otherwise MUST be labelled. Each needs a reachability argument,
#: because two unlabelled values on a co-occurring axis render one title:
#:
#: * ``chat`` and ``image-text-to-text`` are both unlabelled, and would collide
#:   -- except that declaring ``image-text-to-text`` implies the ``vision``
#:   feature (see ``presets._VISION_CAPABILITIES``), so its examples always
#:   carry the ``vision`` qualifier and the pair is unreachable.
#: * ``openai`` is the platform's default dialect; naming it in every title
#:   would say nothing.
#:
#: The corpus check is what proves these arguments still hold. Adding a pair
#: here without one is how a silent overwrite gets introduced.
UNLABELLED: frozenset[tuple[str, str]] = frozenset(
    {
        ("capability", "chat"),
        ("capability", "image-text-to-text"),
        ("dialect", "openai"),
    }
)


#: Label texts an axis may deliberately reuse, with the reachability argument
#: that makes the reuse safe. Same contract as ``UNLABELLED``: a sharing that
#: is not declared here fails the registry check.
#:
#: * ``dashscope`` and ``dashscope_multimodal`` both read "DashScope" because
#:   they name the same provider, and no capability has examples on both of
#:   them (``dashscope`` is embeddings-only; ``dashscope_multimodal`` carries
#:   chat, transcription and speech). Their titles therefore always differ by
#:   the capability qualifier. Adding an embeddings example for
#:   ``dashscope_multimodal`` would break that, and the corpus check -- not
#:   this list -- is what would catch it.
SHARED_LABELS: frozenset[tuple[str, str]] = frozenset(
    {
        ("dialect", "DashScope"),
    }
)


def co_occurs(axis: str) -> bool:
    """Whether two examples differing only on this axis can meet on one service.

    Unknown axes are treated as co-occurring: the safe default is to require
    distinct titles.
    """
    entry = AXES.get(axis)
    return entry.co_occurs if entry else True


def check_registry() -> list[str]:
    """Problems with the registry itself, independent of any example.

    Stated over the declared values rather than the ones in use, so a value
    added with a duplicate or missing label fails before any example adopts it.
    """
    problems: list[str] = []
    for axis_name, axis in sorted(AXES.items()):
        if not axis.co_occurs:
            continue  # titles may coincide; nothing to keep distinct
        by_label: dict[str, list[str]] = {}
        for value, entry in sorted(axis.values.items()):
            if not entry.label:
                if (axis_name, value) not in UNLABELLED:
                    problems.append(
                        f"{axis_name} {value!r} has no display label, so two examples "
                        f"differing only in {axis_name} would render one title and one "
                        f"would silently overwrite the other. Give it a label, or add it "
                        f"to UNLABELLED with the reason the clash is unreachable."
                    )
                continue
            by_label.setdefault(entry.label, []).append(value)
        for label_text, values in sorted(by_label.items()):
            if len(values) > 1 and (axis_name, label_text) not in SHARED_LABELS:
                problems.append(
                    f"{axis_name} values {values} share the display label "
                    f"{label_text!r}; their titles would be identical. A title is a "
                    f"document's key, so the loser is overwritten at ingest. If the "
                    f"clash is unreachable, add it to SHARED_LABELS with the reason."
                )
    return problems


def classifier(axis: str, value: str) -> Classifier:
    """The registry entry for one value.

    Raises:
        KeyError: The axis or the value is not registered. Callers that reach
            here have skipped :func:`validate`, which is the layer meant to
            produce a readable message.
    """
    return AXES[axis].values[value]


def label(axis: str, value: str | None) -> str:
    """How a value reads in a title, or ``""`` when it contributes nothing.

    An unregistered value returns ``""`` rather than raising, so a title is
    never built out of a raw token. Validation is what rejects it; this only
    refuses to leak it.
    """
    if value is None:
        return ""
    axis_entry = AXES.get(axis)
    entry = axis_entry.values.get(value) if axis_entry else None
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
        axis_entry = AXES.get(axis)
        if axis_entry is None:
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
        if value not in axis_entry.values:
            hint = difflib.get_close_matches(value, axis_entry.values, n=1)
            suffix = f" Did you mean {hint[0]!r}?" if hint else ""
            problems.append(
                f"unknown {axis} {value!r}. Register it in "
                f"src/unitysvc_data/classifiers.py (with the label it should "
                f"read as in a title) or fix the spelling.{suffix}"
            )
    return problems
