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
def test_the_alias_resolves_to_the_newest_entry_list():
    """What `llm_example_collection` and every `$doc_preset: llm_request_template`
    get is the newest version, and that is in the entry-list shape."""
    assert ALIASES["llm_request_template"] == "llm_request_template_v4"
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


def test_v4_is_v3_plus_paths_not_rewritten():
    """v3 was published without a path and still works, so the paths arrive as a new
    version rather than an edit (CONTRIBUTING, "The one exception": an amendment needs
    the old behaviour to be gone, and chat's is not). Everything else is v3's, again:
    the bodies, the formats and their order."""
    v3 = _read("llm_request_template_v3")
    v4 = _read("llm_request_template_v4")

    assert _bodies(v4) == _bodies(v3)
    assert [entry["format"] for entry in v4] == [entry["format"] for entry in v3]


def test_the_published_v3_chat_template_is_unchanged():
    """Retired, not edited: a listing that pins v3 gets the entries it was written
    against, and none of them has a path."""
    v3 = _read("llm_request_template_v3")

    assert [entry["format"] for entry in v3] == ["openai", "anthropic", "cohere", "dashscope", "bedrock_converse"]
    assert all("path_suffix" not in entry for entry in v3)


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
    assert [entry["version"] for entry in chat] == [1, 2, 3, 4]


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

#: What each capability's template title reads, pinned because a title is a document's key.
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


# --------------------------------------------------------------------------- #
# Paths: `path_suffix`, read off the example rather than remembered
# --------------------------------------------------------------------------- #
#
# The playground appends a template's `path_suffix` to the service's base URL.
# Without one it sends the body to the base URL itself, which is a 404 for every
# OpenAI-format capability but chat. Each path here is what the example the body
# came from posts to -- those are exercised against real upstreams by `run-tests`,
# so their paths are verified and a path written from knowledge of an API is only
# plausible. All three client variants of an example (requests, shell, JavaScript)
# must agree, which is three independent statements of the same URL.
#
# An entry falls into exactly one of four classes, and only the first has the key:
#   * PATH_FROM          its examples state a path;
#   * BARE               its examples post to the service URL itself, so there is nothing to
#                        append. The page treats a missing or blank `path_suffix` as absent, so
#                        the key is omitted rather than written as "" (or "/", which would add a
#                        trailing slash and so be a different request);
#   * SDK_OWNED          its example hands the base URL to an SDK that appends the path itself,
#                        and the playground's own format registry already carries that path;
#   * SERVICE_DEPENDENT  the path carries the service's own model, so no single string is right
#                        for every service. A KNOWN LIMITATION OF THE CONTRACT (unitysvc#2514,
#                        recorded on unitysvc#2516), not an oversight and not something to work
#                        around in the data.

#: How the OpenAI-shaped examples spell the one segment a seller's upstream may move.
VERSION_PREFIX = "${__version_prefix__}"

#: (capability, format) -> the raw-HTTP examples whose URL the entry's path is.
PATH_FROM = {
    ("chat", "openai"): ["llm_code_example_requests", "llm_code_example_shell", "llm_code_example_javascript"],
    ("chat", "anthropic"): ["llm_code_example_anthropic_shell", "llm_code_example_anthropic_javascript"],
    ("image-text-to-text", "openai"): [
        "llm_code_example_vision_requests",
        "llm_code_example_vision_shell",
        "llm_code_example_vision_javascript",
    ],
    ("embed", "openai"): [
        "llm_code_example_embed_requests",
        "llm_code_example_embed_shell",
        "llm_code_example_embed_javascript",
    ],
    ("embed", "cohere"): [
        "llm_code_example_embed_image_requests",
        "llm_code_example_embed_image_shell",
        "llm_code_example_embed_image_javascript",
    ],
    ("rerank", "openai"): [
        "llm_code_example_rerank_requests",
        "llm_code_example_rerank_shell",
        "llm_code_example_rerank_javascript",
    ],
    ("moderate", "openai"): [
        "llm_code_example_guard_requests",
        "llm_code_example_guard_shell",
        "llm_code_example_guard_javascript",
    ],
    ("image-generate", "openai"): [
        "llm_code_example_image_requests",
        "llm_code_example_image_shell",
        "llm_code_example_image_javascript",
    ],
    ("text-to-speech", "openai"): [
        "llm_code_example_tts_requests",
        "llm_code_example_tts_shell",
        "llm_code_example_tts_javascript",
    ],
}

#: (capability, format) -> the raw-HTTP examples that post to the bare service URL. DashScope's
#: native endpoints are the service URL, so nothing is appended and the entry has no key.
BARE = {
    ("chat", "dashscope"): [
        "llm_code_example_chat_dashscope_text_requests",
        "llm_code_example_chat_dashscope_text_shell",
        "llm_code_example_chat_dashscope_text_javascript",
    ],
    ("embed", "dashscope"): [
        "llm_code_example_embed_dashscope_requests",
        "llm_code_example_embed_dashscope_shell",
        "llm_code_example_embed_dashscope_javascript",
    ],
    ("speech-to-text", "dashscope"): [
        "llm_code_example_asr_dashscope_requests",
        "llm_code_example_asr_dashscope_shell",
        "llm_code_example_asr_dashscope_javascript",
    ],
    ("text-to-speech", "dashscope"): [
        "llm_code_example_tts_dashscope_requests",
        "llm_code_example_tts_dashscope_shell",
        "llm_code_example_tts_dashscope_javascript",
    ],
}

#: (capability, format) -> (example, marker, why). The example hands the base URL to an SDK, which
#: appends the path itself, so the example states none; and the playground's own format registry
#: already carries the native Cohere chat path, so the entry needs no key of its own.
SDK_OWNED = {
    ("chat", "cohere"): (
        "llm_code_example_cohere",
        "cohere.ClientV2(",
        (
            "its only example hands the base URL to the Cohere SDK, which appends the path "
            "itself, and the playground's format registry already carries it"
        ),
    ),
}

#: (capability, format) -> (example, [(scope, marker), ...], why). KNOWN LIMITATION OF THE CONTRACT.
#:
#: The path carries the service's own model, and the right value varies by SERVICE inside the one
#: entry: Hugging Face puts the model name in `/models/<model>`, and Bedrock Converse's depends on
#: the service URL (an interface that already carries `/model/<modelId>` needs only `/converse`,
#: while a shared provider path builds `<service URL>-runtime/model/<modelId>/converse`). A
#: `path_suffix` is one string per (capability, format), so it cannot say "it depends on the
#: service", and the page merges `model` into the body rather than substituting inside the path.
#: Whether `path_suffix` should support substitution is a decision for unitysvc#2514; no syntax
#: is invented here, and these entries omit the key. Each marker is re-checked against the
#: example so the reason cannot go stale.
SERVICE_DEPENDENT = {
    ("chat", "bedrock_converse"): (
        "llm_code_example_bedrock_converse",
        [("source", 'if "/model/" in service_url:'), ("source", 'service_url + "-runtime"')],
        (
            "boto3 builds the path from a service URL whose shape varies by service: a native-runtime "
            "interface already carries /model/<modelId>, a shared provider path does not"
        ),
    ),
    ("embed", "huggingface"): (
        "llm_code_example_sentencetransformers_requests",
        [("path", "routing_key.model")],
        "the example's path ends in the service's own model name",
    ),
    ("video-generate", "huggingface"): (
        "llm_code_example_ttv_requests",
        [("path", "routing_key.model")],
        "the example's path ends in the service's own model name",
    ),
}

_SERVICE_URL = re.compile(r"""["`]\{\{\s*service_base_url\s*\}\}([^"`]*)["`]""")


def _bundled(preset: str) -> str:
    """A preset's file exactly as shipped: placeholders unsubstituted."""
    target = ALIASES.get(preset, preset)
    return (EXAMPLES / MANIFEST["presets"][target]["example_file"]).read_text(encoding="utf-8")


def _example_path(example: str) -> str:
    """What a raw-HTTP example appends to the service's base URL, as written."""
    found = _SERVICE_URL.findall(_bundled(example))
    assert len(found) == 1, f"{example} has {len(found)} service URLs, expected exactly one: {found}"
    return found[0]


def _entries_as_shipped(capability: str) -> list[dict]:
    """The template's entries with the version-prefix placeholder still in them."""
    return json.loads(_bundled(_templates()[capability]))


def _entry(capability: str, fmt: str) -> dict:
    return next(e for e in _entries_as_shipped(capability) if e["format"] == fmt)


def test_every_entry_has_a_path_or_a_recorded_reason_it_has_none():
    pairs = {(c, e["format"]) for c in OFFERED for e in _entries_as_shipped(c)}
    without = {(c, e["format"]) for c in OFFERED for e in _entries_as_shipped(c) if "path_suffix" not in e}

    classes = [set(PATH_FROM), set(BARE), set(SDK_OWNED), set(SERVICE_DEPENDENT)]

    assert pairs == set().union(*classes), "an entry was added or removed: give it a path or a reason"
    assert sum(len(c) for c in classes) == len(pairs), "an entry is in more than one class"
    assert without == set(BARE) | set(SDK_OWNED) | set(SERVICE_DEPENDENT), (
        "exactly the entries without a path omit the key"
    )


@pytest.mark.parametrize(("capability", "fmt"), sorted(PATH_FROM))
def test_a_path_is_the_one_its_examples_post_to(capability, fmt):
    """Not remembered from an API's documentation: read off the examples, all three
    of which (requests, shell, JavaScript) must say the same thing."""
    stated = {example: _example_path(example) for example in PATH_FROM[capability, fmt]}

    assert len(set(stated.values())) == 1, f"the examples disagree about the path: {stated}"
    assert _entry(capability, fmt)["path_suffix"] == next(iter(stated.values()))


@pytest.mark.parametrize(("capability", "fmt"), sorted(SDK_OWNED))
def test_an_sdk_owned_path_is_not_stated_by_its_example(capability, fmt):
    """The example is an SDK call, so there is no URL in it to read a path off, and the key is
    omitted rather than filled from the API's documentation."""
    example, marker, reason = SDK_OWNED[capability, fmt]
    source = _bundled(example)

    assert marker in source, f"{example} no longer contains {marker!r}, so: {reason}"
    assert not any(call in source for call in ("requests.post(", "curl ", "fetch("))
    assert "path_suffix" not in _entry(capability, fmt)


@pytest.mark.parametrize(("capability", "fmt"), sorted(SERVICE_DEPENDENT))
def test_a_service_dependent_path_has_the_reason_it_was_given(capability, fmt):
    """The known limitation, checked against the examples it is about: the path carries the
    service's own model, or is built from a service URL whose shape varies."""
    example, markers, reason = SERVICE_DEPENDENT[capability, fmt]
    haystacks = {"source": _bundled(example), "path": None}
    if any(scope == "path" for scope, _marker in markers):
        haystacks["path"] = _example_path(example)

    for scope, marker in markers:
        assert marker in haystacks[scope], f"{example} no longer has {marker!r} in its {scope}: {reason}"
    assert "path_suffix" not in _entry(capability, fmt)


@pytest.mark.parametrize(("capability", "fmt"), sorted(BARE))
def test_an_entry_that_posts_to_the_bare_service_url_omits_the_key(capability, fmt):
    """DashScope's native endpoints are the service URL itself:
    `requests.post("{{ service_base_url }}", ...)`, in every client variant, and a raw HTTP call
    rather than an SDK that appends something. There is no suffix to append. The page treats a
    missing, blank or non-string `path_suffix` as absent and falls back, so omission is how that is
    said; writing "" adds nothing and "/" is a different request (a trailing slash)."""
    for example in BARE[capability, fmt]:
        source = _bundled(example)
        assert _example_path(example) == "", f"{example} appends something to the service URL"
        assert any(call in source for call in ("requests.post(", "curl ", "fetch(")), (
            f"{example} is not a raw HTTP call, so an empty remainder would mean nothing"
        )
    assert "path_suffix" not in _entry(capability, fmt)


def test_only_dashscope_posts_to_the_bare_service_url():
    """The four are every entry that does, by what the examples do and not by name."""
    assert {fmt for _capability, fmt in BARE} == {"dashscope"}
    assert not any(_example_path(PATH_FROM[pair][0]) == "" for pair in PATH_FROM)


# --- the one segment a seller's upstream may move ------------------------------------
def _moves(pair) -> bool:
    return _example_path(PATH_FROM[pair][0]).startswith(VERSION_PREFIX)


def test_a_template_declares_the_prefix_parameter_exactly_when_a_path_uses_it():
    """The OpenAI-shaped examples build their path from `version_prefix` because a seller's
    upstream may serve that surface elsewhere (Cohere at /compatibility/v1, crofai at /v2, the
    platform facades at ""). A template that omitted it would document those services at a
    path that 404s -- the failure this key exists to end -- so it declares the same parameter
    with the same default the examples declare, and `llm_example_collection` broadcasts the
    listing's value to it as it does to them."""
    for capability, family in _templates().items():
        uses = any(_moves((capability, e["format"])) for e in _entries_as_shipped(capability) if (capability, e["format"]) in PATH_FROM)
        declared = MANIFEST["presets"][ALIASES[family]]["parameters"]

        if not uses:
            assert declared == {}, f"{capability} declares a parameter nothing uses"
            continue
        example_default = MANIFEST["presets"][ALIASES["llm_code_example_requests"]]["parameters"]["version_prefix"]
        assert declared == {"version_prefix": example_default}, capability


def test_without_a_listing_value_every_path_is_the_shared_one():
    """The default is what the design asks for: one customer-facing path per capability and
    format, `/v1/...` for the OpenAI shapes."""
    for (capability, fmt), examples in PATH_FROM.items():
        rendered = next(e for e in _read(_templates()[capability]) if e["format"] == fmt)["path_suffix"]
        written = _example_path(examples[0])

        assert rendered == written.replace(VERSION_PREFIX, "/v1")


def _rendered_paths(prefix: str) -> dict[tuple[str, str], str]:
    docs = llm_example_collection(
        {
            "capabilities": ALL_CAPABILITIES,
            "formats": sorted(ALL_DIALECTS),
            "params": {"version_prefix": prefix},
        }
    )
    out = {}
    for doc in docs.values():
        if doc["category"] != "request_template":
            continue
        capability = doc["meta"]["applies_to"]["capability"]
        for entry in json.loads(Path(doc["file_path"]).read_text(encoding="utf-8")):
            if "path_suffix" in entry:
                out[capability, entry["format"]] = entry["path_suffix"]
    return out


@pytest.mark.parametrize("prefix", ["/v1", "/compatibility/v1", "/v2", ""])
def test_a_listings_prefix_reaches_the_paths_that_move_and_only_those(prefix):
    """What the code examples already do for these listings, the templates now do too.

    Cohere's compatibility surface is /compatibility/v1, crofai's API is /v2, and the
    platform's own facades set it to nothing, so a template that said `/v1/...` would send
    their customers to a path that 404s. Everything the prefix does not belong to -- an
    Anthropic request is `/v1/messages` and a DashScope one is the service URL, whatever the
    seller's OpenAI surface is -- stays exactly where it was."""
    rendered = _rendered_paths(prefix)

    # Only entries that have a path appear: the bare ones (DashScope) never gain a key, whatever the
    # seller's OpenAI surface is, and an empty prefix does not turn one of them into "/".
    assert set(rendered) == set(PATH_FROM)
    assert not any(path in ("", "/") for path in rendered.values())
    for pair, examples in PATH_FROM.items():
        written = _example_path(examples[0])
        expected = prefix + written.removeprefix(VERSION_PREFIX) if written.startswith(VERSION_PREFIX) else written
        assert rendered[pair] == expected, (pair, prefix)


def test_a_translated_format_keeps_its_path_whatever_the_upstream_is():
    """The design point, as the repo already states it. The Anthropic-to-OpenAI example calls
    the OpenAI UPSTREAM at `${version_prefix}/chat/completions` only under `local_testing`; a
    customer calls the gateway at the literal `/v1/messages`, and the gateway translates. So
    for a translated format the path is a function of the capability and the format the
    customer speaks, and of nothing the seller's upstream does."""
    source = _bundled("llm_code_example_anthropic_to_openai_requests")
    local, gateway = source.split("{% else %}")

    assert f'"{{{{ service_base_url }}}}{VERSION_PREFIX}/chat/completions"' in local
    assert '"{{ service_base_url }}/v1/messages"' in gateway
    assert _entry("chat", "anthropic")["path_suffix"] == "/v1/messages"
    for prefix in ("/compatibility/v1", "/v2", ""):
        assert _rendered_paths(prefix)["chat", "anthropic"] == "/v1/messages"
