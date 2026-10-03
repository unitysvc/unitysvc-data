"""The request templates the Test Request playground starts a request from.

The playground picks a document by the capability its ``applies_to`` names, then
the first entry in it that names the format the customer chose
(unitysvc/unitysvc#2514, #2515). So a template is one document per capability,
holding one ``{"format", "body"}`` entry per request format.

This module is about the DATA: what the shipped documents contain and what they
were derived from. The checks that keep a document reachable are in
``tools/build.py`` (``check_request_templates``) and are tested in
``test_build.py``; how titles stay distinct is in ``test_classifiers.py``.
"""

from __future__ import annotations

import base64
import itertools
import json
import re
from pathlib import Path

import pytest

from unitysvc_data import ALIASES, MANIFEST, applies_to, classifiers, doc_preset, llm_example_collection
from unitysvc_data.presets import _select

EXAMPLES = Path(__file__).resolve().parent.parent / "src" / "unitysvc_data" / "examples"


def _read(preset: str):
    """The parsed JSON of a preset's file, alias or pinned version alike."""
    return json.loads(Path(doc_preset(preset)["file_path"]).read_text(encoding="utf-8"))


def _bodies(entries: list[dict]) -> dict[str, dict]:
    return {entry["format"]: entry["body"] for entry in entries}


# --------------------------------------------------------------------------- #
# The chat template: migrated in shape, not rewritten
# --------------------------------------------------------------------------- #
def test_the_alias_resolves_to_the_entry_list():
    """What `llm_example_collection` and every `$doc_preset: llm_request_template`
    get is the newest version, and that is the one in the new shape."""
    assert ALIASES["llm_request_template"] == "llm_request_template_v3"
    assert isinstance(_read("llm_request_template"), list)


def test_v3_is_v2_repackaged_not_rewritten():
    """The issue's acceptance criterion for chat is that it behaves identically.
    A migration that quietly improved a prompt on the way through would not, so
    this pins the bodies, the formats and their order against the version they
    replace."""
    v2 = _read("llm_request_template_v2")
    v3 = _read("llm_request_template_v3")

    assert _bodies(v3) == v2
    assert [entry["format"] for entry in v3] == list(v2)


def test_every_chat_entry_is_a_format_the_gateway_names():
    """The gateway's own vocabulary for the formats chat bodies are written in
    (apisix-gateways `request_meta`), not the finer dialect tokens the code
    examples use: `dashscope`, not `dashscope_text` / `dashscope_multimodal`."""
    formats = [entry["format"] for entry in _read("llm_request_template")]

    assert formats == ["openai", "anthropic", "cohere", "dashscope", "bedrock_converse"]


def test_chat_is_served_by_one_family_and_it_names_chat():
    chat = [
        entry
        for key, entry in MANIFEST["presets"].items()
        if key.startswith("llm_request_template") and entry["applies_to"].get("capability") == "chat"
    ]

    assert {entry["preset_name"] for entry in chat} == {"llm_request_template"}
    assert [entry["version"] for entry in chat] == [1, 2, 3]


# --------------------------------------------------------------------------- #
# What is shipped, capability by capability
# --------------------------------------------------------------------------- #

#: capability -> the request formats its template carries, in order.
#:
#: Each entry is the request a code example sends (see ``DERIVED_FROM``), so this
#: is not a wish list: a (capability, format) pair is here because an example for
#: it exists AND can be written as a JSON body. The chat row is v2's, unchanged.
OFFERED = {
    "chat": ["openai", "anthropic", "cohere", "dashscope", "bedrock_converse"],
    "image-text-to-text": ["openai"],
    "embed": ["openai", "cohere", "dashscope", "huggingface"],
    "rerank": ["openai"],
    "moderate": ["openai"],
    "image-generate": ["openai"],
    "video-generate": ["huggingface"],
    "speech-to-text": ["dashscope"],
    "text-to-speech": ["openai", "dashscope"],
}

#: capability -> why it has no template. An absent template is the playground's
#: honest empty state; a template that cannot be sent is worse than none. Each
#: reason is checked against the examples below, so it cannot go stale: the day an
#: example becomes a JSON body, that test fails and says to write the template.
NO_TEMPLATE = {
    "image-edit": "its only code example (dialect huggingface) sends multipart/form-data, "
    "which an entry's JSON body cannot express",
}

#: What each non-chat title reads, pinned because a title is a document's key.
TITLES = {
    "chat": "Default request body",
    "image-text-to-text": "Default request body (vision)",
    "embed": "Default request body (embeddings)",
    "rerank": "Default request body (rerank)",
    "moderate": "Default request body (moderation)",
    "image-generate": "Default request body (image)",
    "video-generate": "Default request body (video)",
    "speech-to-text": "Default request body (transcription)",
    "text-to-speech": "Default request body (speech)",
}


def _families() -> dict[str, set[str]]:
    """capability -> the request-template families (preset names) that name it."""
    out: dict[str, set[str]] = {}
    for key, entry in MANIFEST["presets"].items():
        if key.startswith("llm_") and entry["category"] == "request_template":
            capability = entry["applies_to"].get("capability")
            out.setdefault(capability, set()).add(entry["preset_name"])
    return out


def _templates() -> dict[str, str]:
    """capability -> its one template family."""
    return {capability: next(iter(names)) for capability, names in _families().items()}


def test_every_capability_is_either_served_or_exempt_with_a_reason():
    registered = set(classifiers.CAPABILITIES)

    assert set(OFFERED) | set(NO_TEMPLATE) == registered, (
        "a capability was added or removed: give it a template, or an entry in NO_TEMPLATE"
    )
    assert not set(OFFERED) & set(NO_TEMPLATE), "a capability cannot be both served and exempt"


def test_each_capability_has_exactly_one_request_template_family():
    """The per-capability form of "exactly one template serves chat". Two families
    for one capability would both be selected for it, render the same title, and
    leave whichever sorts last as the only one that survives."""
    families = _families()

    assert set(families) == set(OFFERED)
    assert {capability: len(names) for capability, names in families.items()} == {
        capability: 1 for capability in OFFERED
    }


def test_the_exempt_capabilities_have_no_template():
    assert not set(_families()) & set(NO_TEMPLATE)


def test_each_template_offers_exactly_the_formats_derived_for_it():
    for capability, preset in _templates().items():
        assert [entry["format"] for entry in _read(preset)] == OFFERED[capability], capability


def test_a_template_applies_to_its_capability_and_nothing_else():
    """The brief for the ten: `applies_to = { capability = ... }`, uniformly. A
    template bundles every format, so a dialect would make it exclude the very
    services it is written for; the playground matches on capability alone."""
    for capability, preset in _templates().items():
        assert applies_to(preset) == {"capability": capability}


def test_no_body_names_a_model():
    """The playground merges the service's routing key into the body it sends."""
    for capability, preset in _templates().items():
        for entry in _read(preset):
            assert "model" not in entry["body"], f"{capability}/{entry['format']} names a model"


def test_every_format_is_a_registered_dialect():
    """The build checks this too; the corpus statement of it, so a hand-edited
    manifest cannot slip an unreachable entry past a stale build."""
    for capability, preset in _templates().items():
        for entry in _read(preset):
            assert entry["format"] in classifiers.DIALECTS, f"{capability}: {entry['format']!r}"


@pytest.mark.parametrize("capability", sorted(NO_TEMPLATE))
def test_an_exemption_still_holds_for_every_example_it_names(capability):
    """The reason is a claim about the code examples, so check the claim. If one
    becomes a JSON body there is a template to write, and this says so."""
    markers = ("files=", "FormData", " -F ")
    examples = [
        entry
        for key, entry in MANIFEST["presets"].items()
        if key.startswith("llm_code_example")
        and entry["applies_to"].get("capability") == capability
    ]
    assert examples, f"{capability} has no code examples at all"

    latest = {}
    for entry in examples:
        if entry["version"] >= latest.get(entry["preset_name"], (0, ""))[0]:
            latest[entry["preset_name"]] = (entry["version"], entry["example_file"])
    for name, (_version, relative) in sorted(latest.items()):
        source = (EXAMPLES / relative).read_text(encoding="utf-8")
        assert any(marker in source for marker in markers), (
            f"{name} no longer sends multipart/form-data, so {capability} can have a template: "
            f"{NO_TEMPLATE[capability]}"
        )


# --------------------------------------------------------------------------- #
# Selection: no new code, verified
# --------------------------------------------------------------------------- #
ALL_DIALECTS = set(classifiers.DIALECTS)
DIALECT_SETS = [set(), {"openai"}, {"anthropic"}, {"dashscope_audio_task"}, {"huggingface"}, ALL_DIALECTS]
FEATURE_SETS = [set(), {"streaming"}, {"streaming", "tools"}, {"streaming", "tools", "vision"}]


@pytest.mark.parametrize("capability", sorted(OFFERED))
def test_a_template_is_selected_for_its_capability_whatever_else_the_service_is(capability):
    """`_applies` treats an absent key as no constraint, so a template that names
    only its capability needs no selection code. That is a claim about every
    service, so it is checked over every combination of dialects, upstream and
    features rather than the one that happens to be convenient."""
    templates = set(_templates().values())
    mine = _templates()[capability]

    for dialects, upstream, features in itertools.product(
        DIALECT_SETS, ("openai", "anthropic", "dashscope"), FEATURE_SETS
    ):
        selected = {
            name
            for _title, name in _select(
                capability=capability, dialects=dialects, upstream=upstream, features=features
            )
            if name in templates
        }
        assert selected == {mine}, (capability, dialects, upstream, features, selected)


@pytest.mark.parametrize("capability", sorted(NO_TEMPLATE))
def test_an_exempt_capability_selects_no_template(capability):
    templates = set(_templates().values())

    for dialects, features in itertools.product(DIALECT_SETS, FEATURE_SETS):
        selected = {
            name
            for _title, name in _select(
                capability=capability, dialects=dialects, upstream="openai", features=features
            )
            if name in templates
        }
        assert not selected, (capability, dialects, features, selected)


# --------------------------------------------------------------------------- #
# Titles: the pin, end to end
# --------------------------------------------------------------------------- #
def _template_docs(docs: dict) -> dict[str, str]:
    """capability -> title, for the request templates in a collection."""
    return {
        doc["meta"]["applies_to"]["capability"]: title
        for title, doc in docs.items()
        if doc["category"] == "request_template"
    }


ALL_CAPABILITIES = sorted(classifiers.CAPABILITIES)


@pytest.mark.parametrize("pair", list(itertools.combinations(ALL_CAPABILITIES, 2)), ids="+".join)
def test_a_service_declaring_two_capabilities_keeps_both_templates(pair):
    """The failure this exists to prevent, for every pair. `docs` is keyed by title,
    so two templates that rendered one title would leave only the second -- and
    for chat and image-text-to-text they did, until the registry said what carries
    the latter. A test over the real selector, not the title function alone: it
    fails on the title builder as it was before `carried_by`."""
    docs = llm_example_collection({"capabilities": list(pair), "formats": ["openai"]})

    assert _template_docs(docs) == {c: TITLES[c] for c in pair if c in TITLES}


def test_a_service_declaring_every_capability_gets_one_distinct_template_each():
    docs = llm_example_collection(
        {"capabilities": ALL_CAPABILITIES, "formats": sorted(ALL_DIALECTS)}
    )

    found = _template_docs(docs)
    assert found == TITLES
    assert len(set(found.values())) == len(found), "two templates share a title"
    # Nothing was overwritten on the way: every template the selector produced is here.
    selected = [
        (title, name)
        for capability in ALL_CAPABILITIES
        for title, name in _select(
            capability=capability,
            dialects=ALL_DIALECTS,
            upstream="openai",
            features={"streaming", "vision"},
        )
        if name in set(_templates().values())
    ]
    assert len(selected) == len(found) == len({title for title, _name in selected})


def test_chat_keeps_the_title_listings_key_their_own_entry_to():
    """Hand-written listings carry `"Default request body": {"$doc_preset":
    "llm_request_template"}`, so this string is part of the public surface."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert _template_docs(docs) == {"chat": "Default request body"}


# --------------------------------------------------------------------------- #
# Derivation: the bodies are the examples', not new ones
# --------------------------------------------------------------------------- #

#: (capability, format) -> the code example whose request the body is. Chat is not
#: here: its bodies are v2's, pinned against v2 above, and they predate this rule.
DERIVED_FROM = {
    ("image-text-to-text", "openai"): "llm_code_example_vision_requests",
    ("embed", "openai"): "llm_code_example_embed_requests",
    ("embed", "cohere"): "llm_code_example_embed_image_requests",
    ("embed", "dashscope"): "llm_code_example_embed_dashscope_requests",
    ("embed", "huggingface"): "llm_code_example_sentencetransformers_requests",
    ("rerank", "openai"): "llm_code_example_rerank_requests",
    ("moderate", "openai"): "llm_code_example_guard_requests",
    ("image-generate", "openai"): "llm_code_example_image_requests",
    ("video-generate", "huggingface"): "llm_code_example_ttv_requests",
    ("speech-to-text", "dashscope"): "llm_code_example_asr_dashscope_requests",
    ("text-to-speech", "openai"): "llm_code_example_tts_requests",
    ("text-to-speech", "dashscope"): "llm_code_example_tts_dashscope_requests",
}

#: The code examples name finer dialects than the gateway has formats: three
#: DashScope surfaces, one `dashscope` format. A format is derived from an example
#: whose dialect is any of these.
DIALECTS_OF_FORMAT = {"dashscope": {"dashscope", "dashscope_audio_task"}}

IMAGE = (EXAMPLES / "llm" / "test-image.jpg").read_bytes()


def _all_pairs() -> list[tuple[str, str]]:
    return [(c, f) for c, formats in OFFERED.items() if c != "chat" for f in formats]


def test_every_non_chat_pair_names_the_example_it_came_from():
    assert sorted(DERIVED_FROM) == sorted(_all_pairs())


@pytest.mark.parametrize(("capability", "fmt"), sorted(DERIVED_FROM))
def test_the_example_is_for_that_capability_and_format(capability, fmt):
    spec = applies_to(DERIVED_FROM[capability, fmt])

    assert spec["capability"] == capability
    assert spec["dialect"] in DIALECTS_OF_FORMAT.get(fmt, {fmt})


def _keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _keys(value)
    elif isinstance(node, list):
        for item in node:
            yield from _keys(item)


def _scalars(node, key=None):
    """(nearest dict key, scalar) for every leaf."""
    if isinstance(node, dict):
        for k, value in node.items():
            yield from _scalars(value, k)
    elif isinstance(node, list):
        for item in node:
            yield from _scalars(item, key)
    else:
        yield key, node


@pytest.mark.parametrize(("capability", "fmt"), sorted(DERIVED_FROM))
def test_every_key_and_value_of_a_body_is_in_the_example_it_came_from(capability, fmt):
    """Do not invent the bodies. The examples are what `run-tests` sends to real
    upstreams, so a key or a string that appears in the body but not in its example
    is one nobody has verified. This is deliberately a check on the words, not a
    parse of the example: the examples are Jinja templates with variables in them,
    and a parser would be a second thing to keep in step with them."""
    example = DERIVED_FROM[capability, fmt]
    source = Path(doc_preset(example)["file_path"]).read_text(encoding="utf-8")
    entry = next(e for e in _read(_templates()[capability]) if e["format"] == fmt)

    for key in _keys(entry["body"]):
        assert f'"{key}"' in source, f"key {key!r} is not in {example}"
    for key, value in _scalars(entry["body"]):
        if isinstance(value, str):
            if value.startswith("data:image/"):
                continue  # the inlined test image; checked on its own below
            assert value in source, f"{value!r} is not in {example}"
        elif isinstance(value, bool):
            continue
        elif isinstance(value, (int, float)):
            assert re.search(rf'"{re.escape(key)}"\s*:\s*{value}\b', source), (
                f"{key} = {value} is not in {example}"
            )


@pytest.mark.parametrize(
    ("capability", "fmt"), [("image-text-to-text", "openai"), ("embed", "cohere")]
)
def test_the_inlined_image_is_the_one_the_examples_fetch(capability, fmt):
    """The examples inline `llm/test-image.jpg` as a data URI -- the vision one
    explains why: handing a provider a URL leaves it to fetch the bytes itself. The
    template carries exactly those bytes, so it is the request that was run."""
    entry = next(e for e in _read(_templates()[capability]) if e["format"] == fmt)
    uris = [v for _k, v in _scalars(entry["body"]) if isinstance(v, str) and v.startswith("data:")]

    assert len(uris) == 1
    header, payload = uris[0].split(",", 1)
    assert header == "data:image/jpeg;base64"
    assert base64.b64decode(payload) == IMAGE
