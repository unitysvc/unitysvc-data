"""How a document's title is built from its classifiers.

Separate from :mod:`unitysvc_data.presets` so ``tools/build.py`` can render a
title while validating, without importing the module that loads the manifest
that same script generates.

A title is a document's KEY: the backend upserts on
``(entity_id, context_type, title)``, so two examples that render one title do
not conflict -- the second overwrites the first and the example is lost with no
signal. Everything here exists to keep that from happening quietly.
"""

from __future__ import annotations

from typing import Any

from . import classifiers

#: Document title by mime type. Several flavours can share a language, so
#: the dialect and feature qualify it where needed.
_TITLE_BY_MIME = {
    "python": "Python code example",
    "javascript": "JavaScript code example",
    "bash": "cURL code example",
}

#: Titles for the non-example documents, by category.
_TITLE_BY_CATEGORY = {
    "connectivity_test": "Connectivity test",
    "request_template": "Default request body",
    "getting_started": "How to use this model",
}


def title(entry: dict[str, Any], spec: dict[str, Any]) -> str:
    """A distinct, customer-facing title for one document."""
    category = entry["category"]
    # Non-example documents get a fixed base title, but still need the
    # qualifier: a service can legitimately match two probes (a cohere
    # embedding service matches both the OpenAI-compat and the
    # Cohere-native image probe), and a fixed title would drop one.
    base = _TITLE_BY_CATEGORY.get(category) or _TITLE_BY_MIME.get(
        entry["mime_type"], entry["mime_type"]
    )
    bits = []
    # The capability first, because it is the most significant distinction: an
    # omni model declaring chat, text-to-speech and speech-to-text used to ship
    # ONE of those three sets of examples, the other two overwritten by title.
    #
    # Every label comes from ``classifiers``, so a value cannot reach a title
    # without being registered -- which is what stops a raw token appearing in
    # front of a customer. An empty label means the value contributes nothing,
    # and the registry records why next to the value.
    if capability_label := classifiers.label("capability", spec.get("capability")):
        bits.append(capability_label)
    dialect = spec.get("dialect")
    dialect_label = classifiers.label("dialect", dialect)
    if dialect_label:
        # "Anthropic-style input" reads as the dialect the CALLER writes;
        # a named SDK reads as itself.
        bits.append(
            f"{dialect_label} input"
            if classifiers.is_caller_dialect(dialect)
            else dialect_label
        )
    # The feature the document declares, then the one its capability is carried
    # by. The second is what keeps an unlabelled capability apart from a bare
    # sibling for a document that declares no feature of its own -- a request
    # template -- instead of leaving that to the document's author. Each is
    # rendered once: an image-text-to-text example declares ``vision`` itself and
    # must not read "(vision, vision)", because a changed title is a different
    # document.
    features: list[str] = []
    for feature in (spec.get("feature"), classifiers.carried_by("capability", spec.get("capability"))):
        if feature and feature not in features:
            features.append(feature)
    for feature in features:
        if feature_label := classifiers.label("feature", feature):
            bits.append(feature_label)
    # Disambiguate SDK-vs-raw within one language — unless the dialect
    # label already names the client.
    if category == "code_example" and not ("SDK" in dialect_label or "boto3" in dialect_label):
        reqs = (entry.get("meta") or {}).get("requirements") or []
        for sdk in ("openai", "anthropic", "cohere", "requests", "boto3"):
            if sdk in reqs:
                bits.append("requests" if sdk == "requests" else f"{sdk} SDK")
                break
    return f"{base} ({', '.join(bits)})" if bits else base
