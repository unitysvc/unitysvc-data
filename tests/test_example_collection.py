"""Tests for ``llm_example_collection`` — the preset that expands a
service's (capability x format) declaration into a whole ``documents``
block, rather than a single document.

Records are compared against ``doc_preset(<name>)`` rather than by
inspecting ``file_path``: the collection must not invent its own record
shape, and ``llm_description`` resolves to a bundled path that does not
carry its preset name, so the path is not a usable key.
"""

from __future__ import annotations

import pytest

from unitysvc_data import doc_preset, llm_example_collection


def presets_in(docs: dict) -> set[str]:
    """The preset names behind ``docs``, by matching whole records.

    Compares against every ``llm_*`` preset so a wrong-but-plausible
    record (right category, wrong body) cannot pass as the right one.
    """
    from unitysvc_data import PRESETS

    # Every llm_* preset expands cleanly; if one ever stops doing so that
    # is a manifest bug and should surface here rather than be swallowed.
    by_record = {_key(doc_preset(name)): name for name in PRESETS if name.startswith("llm_")}
    found = set()
    for record in docs.values():
        name = by_record.get(_key(record))
        assert name is not None, f"record matches no llm_* preset: {record!r}"
        found.add(name)
    return found


def _key(record: dict) -> tuple:
    """Identity of a document record, ignoring caller-supplied meta.

    ``meta`` carries per-call additions (sleep_after_test, channels), so
    it is excluded; everything else must come from the preset verbatim.
    """
    return (record["category"], record["description"], record["file_path"], record["mime_type"])


def examples_in(docs: dict) -> set[str]:
    return presets_in({t: d for t, d in docs.items() if d["category"] == "code_example"})


def test_chat_openai_collection_probes_with_llm_connectivity():
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    probes = [d for d in docs.values() if d["category"] == "connectivity_test"]
    assert len(probes) == 1, "a collection declares exactly one connectivity probe"
    assert _key(probes[0]) == _key(doc_preset("llm_connectivity"))


def test_openai_format_contributes_every_openai_native_flavour():
    """Both SDK and raw styles, in all three languages, plus streaming.

    The superset is deliberate: style is not a fact about the service, so
    the collection emits every flavour rather than curating one per repo.
    """
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert examples_in(docs) == {
        "llm_code_example_openai",  # python, openai SDK
        "llm_code_example_requests",  # python, requests
        "llm_code_example_javascript",  # js, fetch
        "llm_code_example_openai_javascript",  # js, openai SDK
        "llm_code_example_shell",  # curl
        "llm_code_example_streaming_openai",  # python, streaming
        "llm_code_example_streaming_openai_javascript",  # js, streaming
    }


def test_embed_capability_probes_embeddings_not_chat():
    """The probe follows the capability, not the format.

    This is the bug the capability sweep found in four repos: an
    embedding service shipping ``llm_connectivity``, which POSTs a
    chat-completion body that /v1/embeddings rejects — so the declared
    capability was gated by a probe it could never pass.
    """
    docs = llm_example_collection({"capabilities": ["embed"], "formats": ["openai"]})

    probes = [d for d in docs.values() if d["category"] == "connectivity_test"]
    assert _key(probes[0]) == _key(doc_preset("llm_connectivity_embed"))


def test_embed_capability_emits_embedding_examples_only():
    """A chat example on an embedding service fails and blocks activation,
    so the chat flavours must not leak in via the format."""
    docs = llm_example_collection({"capabilities": ["embed"], "formats": ["openai"]})

    assert examples_in(docs) == {
        "llm_code_example_embed_requests",
        "llm_code_example_embed_javascript",
        "llm_code_example_embed_shell",
    }


def test_anthropic_caller_on_an_openai_upstream_gets_translated_examples():
    """The gateway translates, so the example must show the caller's
    dialect going in — not the upstream's."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": "openai"}
    )

    assert examples_in(docs) >= {
        "llm_code_example_anthropic_to_openai_sdk",
        "llm_code_example_anthropic_to_openai_requests",
        "llm_code_example_anthropic_to_openai_shell",
    }
    assert not any(n.startswith("llm_code_example_openai_to_anthropic") for n in examples_in(docs))


def test_anthropic_upstream_inverts_the_translation_and_the_probe():
    """The anthropic repo is the mirror image: its upstream speaks
    Anthropic, so an OpenAI-dialect caller is the one being translated,
    and the probe is the Anthropic-shaped one."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "upstream_dialect": "anthropic"}
    )

    assert examples_in(docs) >= {
        "llm_code_example_openai_to_anthropic_sdk",
        "llm_code_example_openai_to_anthropic_requests",
        "llm_code_example_openai_to_anthropic_shell",
    }
    probes = [d for d in docs.values() if d["category"] == "connectivity_test"]
    assert _key(probes[0]) == _key(doc_preset("llm_connectivity_anthropic"))


def test_native_anthropic_caller_on_an_anthropic_upstream_is_not_translated():
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": "anthropic"}
    )

    assert examples_in(docs) >= {
        "llm_code_example_anthropic",
        "llm_code_example_anthropic_javascript",
        "llm_code_example_anthropic_shell",
    }
    assert not any("_to_" in n for n in examples_in(docs))


def test_function_calling_example_is_gated_on_tool_support():
    """`fc_requests` 400s on a model without tools, and a failing code
    example blocks activation — so this is applicability, not flavour."""
    without = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})
    with_tools = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "tools": True}
    )

    assert "llm_code_example_fc_requests" not in examples_in(without)
    assert "llm_code_example_fc_requests" in examples_in(with_tools)


BEDROCK = {
    "capabilities": ["chat"],
    "formats": [
        {"formats": ["openai"], "channel": "byok", "interface": "provider_api", "primary": True},
        {"formats": ["bedrock_converse"], "channel": "converse", "interface": "converse_api"},
    ],
}


def test_format_groups_scope_their_documents_to_a_channel_and_interface():
    """Bedrock's converse_api resolves to the native runtime URL, so an
    unscoped boto3 example 503s against the provider_api URL."""
    docs = llm_example_collection(BEDROCK)

    converse = docs["Python code example (boto3 Converse)"]
    assert converse["meta"]["channels"] == ["converse"]
    assert converse["meta"]["interfaces"] == ["converse_api"]

    openai = docs["Python code example (openai SDK)"]
    assert openai["meta"]["channels"] == ["byok"]
    assert openai["meta"]["interfaces"] == ["provider_api"]


def test_the_probe_attaches_to_the_primary_group():
    docs = llm_example_collection(BEDROCK)

    probe = next(d for d in docs.values() if d["category"] == "connectivity_test")
    assert probe["meta"]["channels"] == ["byok"]
    assert probe["meta"]["interfaces"] == ["provider_api"]


def test_scoping_preserves_the_presets_own_meta():
    """`requirements` comes from the preset and is what the runner
    installs; clobbering it with scope would break execution."""
    docs = llm_example_collection(BEDROCK)

    assert docs["Python code example (openai SDK)"]["meta"]["requirements"] == ["openai"]


def test_a_plain_format_list_is_one_unscoped_group():
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert "channels" not in docs["Python code example (openai SDK)"]["meta"]


def test_chat_collection_carries_the_description_and_request_template():
    """Both are in 9 of 16 repos today and absent from the rest with no
    reason — normalising means every chat service gets them."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert presets_in(docs) >= {"llm_description", "llm_request_template"}


def test_anthropic_upstream_gets_the_anthropic_request_template():
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": "anthropic"}
    )

    assert "llm_request_template_anthropic" in presets_in(docs)
    assert "llm_request_template" not in presets_in(docs)


def test_sleep_is_applied_to_every_executable_document():
    """Rate-limit spacing is a per-provider fact, and it has to reach the
    probe as well as the examples."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "sleep": 5}
    )

    executable = [
        d for d in docs.values() if d["category"] in ("code_example", "connectivity_test")
    ]
    assert executable, "expected executable documents"
    assert all(d["meta"]["sleep_after_test"] == 5 for d in executable)


def test_sleep_does_not_clobber_the_presets_requirements():
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "sleep": 5}
    )

    assert docs["Python code example (openai SDK)"]["meta"]["requirements"] == ["openai"]


def test_registered_as_a_jinja_global_for_templated_repos():
    """Templated seller repos call it as a Jinja global rather than via
    the JSON sentinel, so it must be registered on the render env."""
    from unitysvc_data import register_jinja_globals

    class Env:
        def __init__(self) -> None:
            self.globals: dict = {}

    env = Env()
    register_jinja_globals(env)
    assert "llm_example_collection" in env.globals


def test_every_document_has_a_distinct_title():
    """Titles are the keys of the ``documents`` mapping, so a collision
    would silently drop an example rather than fail."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert len(docs) == len({_key(d) for d in docs.values()})


def test_multiple_capabilities_are_rejected_rather_than_losing_a_probe():
    """Each capability needs its own probe, but a collection declares one.
    Silently keeping the last would leave a capability unproven — the
    exact failure this preset exists to prevent."""
    with pytest.raises(ValueError, match="one capability"):
        llm_example_collection({"capabilities": ["chat", "embed"], "formats": ["openai"]})


def test_speech_transcribe_is_supported_since_its_presets_exist():
    """Found by the before/after sweep: three services (cohere-transcribe,
    groq whisper x2) were rejected even though unitysvc-data ships both
    the examples and the probe."""
    docs = llm_example_collection({"capabilities": ["speech-transcribe"], "formats": ["openai"]})

    probe = next(d for d in docs.values() if d["category"] == "connectivity_test")
    assert _key(probe) == _key(doc_preset("llm_connectivity_transcription"))
    assert examples_in(docs) == {
        "llm_code_example_transcription_requests",
        "llm_code_example_transcription_javascript",
        "llm_code_example_transcription_shell",
    }


def test_the_how_to_use_doc_is_emitted_for_every_capability():
    """Found by the sweep: 12 embedding services lost `llm_description`.
    It describes how ANY LLM service is consumed through the gateway, so
    it is not chat-specific."""
    for capability in ("chat", "embed", "speech-transcribe"):
        docs = llm_example_collection({"capabilities": [capability], "formats": ["openai"]})
        assert "llm_description" in presets_in(docs), capability


def test_cerebras_dialect_contributes_its_sdk_example():
    """Found by the sweep: cerebras' three services lost their SDK example
    because the dialect had no entry."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai", "cerebras"]})

    assert "llm_code_example_cerebras" in examples_in(docs)


#: capability -> the COMPLETE set of examples it must emit, and the
#: connectivity preset that proves it (``None`` where none is authored
#: yet). Written out in full rather than derived from ``meta.variant``:
#: the implementation derives from that, so deriving here too would make
#: the test tautological and blind to a mapping regression.
CAPABILITY_CONTRACT = {
    "embed": (
        {
            "llm_code_example_embed_requests",
            "llm_code_example_embed_javascript",
            "llm_code_example_embed_shell",
        },
        "llm_connectivity_embed",
    ),
    "speech-transcribe": (
        {
            "llm_code_example_transcription_requests",
            "llm_code_example_transcription_javascript",
            "llm_code_example_transcription_shell",
        },
        "llm_connectivity_transcription",
    ),
    "speech-synthesize": (
        {
            "llm_code_example_tts_requests",
            "llm_code_example_tts_javascript",
            "llm_code_example_tts_shell",
        },
        None,
    ),
    "video-generate": (
        {
            "llm_code_example_ttv_requests",
            "llm_code_example_ttv_javascript",
            "llm_code_example_ttv_shell",
        },
        None,
    ),
    "image-generate": (
        {
            "llm_code_example_image_requests",
            "llm_code_example_image_javascript",
            "llm_code_example_image_shell",
        },
        None,
    ),
    "image-edit": (
        {
            "llm_code_example_imagetoimage_requests",
            "llm_code_example_imagetoimage_javascript",
            "llm_code_example_imagetoimage_shell",
        },
        None,
    ),
    "rerank": (
        {
            "llm_code_example_rerank_requests",
            "llm_code_example_rerank_javascript",
            "llm_code_example_rerank_shell",
        },
        None,
    ),
    "moderate": (
        {
            "llm_code_example_guard_requests",
            "llm_code_example_guard_javascript",
            "llm_code_example_guard_shell",
        },
        None,
    ),
}


@pytest.mark.parametrize("capability", sorted(CAPABILITY_CONTRACT))
def test_a_capability_emits_its_complete_example_set(capability):
    """All three language flavours, not just one.

    Every code-example preset declares the capability it demonstrates in
    `meta.variant`, so a capability is expressible as soon as its examples
    exist — a dedicated connectivity preset is a separate concern.
    """
    expected, _ = CAPABILITY_CONTRACT[capability]
    docs = llm_example_collection({"capabilities": [capability], "formats": ["openai"]})

    assert examples_in(docs) == expected


@pytest.mark.parametrize("capability", sorted(CAPABILITY_CONTRACT))
def test_a_capability_offers_every_language(capability):
    """python / javascript / bash, so no caller is left without one."""
    docs = llm_example_collection({"capabilities": [capability], "formats": ["openai"]})

    mimes = {d["mime_type"] for d in docs.values() if d["category"] == "code_example"}
    assert mimes == {"python", "javascript", "bash"}


@pytest.mark.parametrize("capability", sorted(CAPABILITY_CONTRACT))
def test_the_probe_matches_the_capability_contract(capability):
    """Where a probe is authored the capability gets it; where none is,
    the collection emits NO connectivity document rather than falling back
    to a chat probe that cannot pass. `specs validate` and the activation
    gate then reject the service at the point of declaration."""
    _, probe = CAPABILITY_CONTRACT[capability]
    docs = llm_example_collection({"capabilities": [capability], "formats": ["openai"]})

    emitted = [d for d in docs.values() if d["category"] == "connectivity_test"]
    if probe is None:
        assert emitted == []
    else:
        assert len(emitted) == 1
        assert _key(emitted[0]) == _key(doc_preset(probe))


def test_capabilities_whose_probe_exists_still_get_one():
    for capability, probe in [
        ("chat", "llm_connectivity"),
        ("embed", "llm_connectivity_embed"),
        ("speech-transcribe", "llm_connectivity_transcription"),
    ]:
        docs = llm_example_collection({"capabilities": [capability], "formats": ["openai"]})
        assert probe in presets_in(docs), capability


def test_an_unrecognised_capability_is_still_an_error():
    with pytest.raises(ValueError, match="ocr"):
        llm_example_collection({"capabilities": ["ocr"], "formats": ["openai"]})


def test_every_llm_code_example_declares_what_it_applies_to():
    """`applies_to` is the systematic representation: each example states
    the capability it demonstrates, and for chat the caller dialect and
    upstream dialect it targets. Selection reads this rather than pattern
    matching on preset names or mapping free-text `variant` labels.
    """
    from unitysvc_data import MANIFEST, applies_to

    missing = []
    for key, entry in MANIFEST["presets"].items():
        if not key.startswith("llm_") or entry["category"] != "code_example":
            continue
        spec = applies_to(entry.get("preset_name", key))
        if not spec.get("capability"):
            missing.append(key)
    assert not missing, f"code examples with no declared capability: {missing}"


def test_chat_examples_declare_both_dialect_and_upstream():
    """`variant='Chat'` covers both OpenAI-native and Anthropic-native
    presets with nothing to tell them apart — which is why chat needed a
    hand-written map. `applies_to` records the pair."""
    from unitysvc_data import applies_to

    assert applies_to("llm_code_example_openai")["dialect"] == "openai"
    assert applies_to("llm_code_example_openai")["upstream"] == "openai"
    assert applies_to("llm_code_example_anthropic")["dialect"] == "anthropic"
    assert applies_to("llm_code_example_anthropic")["upstream"] == "anthropic"
    # translated: caller writes Anthropic, upstream speaks OpenAI
    spec = applies_to("llm_code_example_anthropic_to_openai_sdk")
    assert (spec["dialect"], spec["upstream"]) == ("anthropic", "openai")


def test_attribute_gated_examples_declare_their_feature():
    from unitysvc_data import applies_to

    assert applies_to("llm_code_example_fc_requests")["feature"] == "tools"
    assert applies_to("llm_code_example_streaming_openai")["feature"] == "streaming"


def test_applies_to_never_leaks_into_the_document_record():
    """Selection metadata is build-time; the record describes the
    listing-document. Same rule `parameters` already follows."""
    assert "applies_to" not in doc_preset("llm_code_example_openai")


@pytest.mark.parametrize(
    "source",
    [
        {"capabilities": ["chat"], "formats": ["openai"]},
        {"capabilities": ["chat"], "formats": ["openai", "anthropic"], "tools": True},
        {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": "openai"},
        {"capabilities": ["chat"], "formats": ["openai"], "upstream_dialect": "anthropic"},
        {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": "anthropic"},
        {"capabilities": ["chat"], "formats": ["openai", "cohere", "cerebras"]},
        BEDROCK,
    ],
    ids=["openai", "both+tools", "anth->openai", "openai->anth", "anth-native", "sdks", "bedrock"],
)
def test_no_two_examples_collide_on_a_title(source):
    """Titles are the keys of `documents`, so a collision silently drops an
    example. The sdk-vs-requests pair renders in the same language and the
    same dialect, so it is the case most likely to collapse."""
    docs = llm_example_collection(source)

    assert len(docs) == len({_key(d) for d in docs.values()})


def test_the_probe_is_selected_like_everything_else():
    """No hand-maintained capability->probe table: connectivity presets
    declare `applies_to` just as examples do, so the right probe falls out
    of the same query."""
    from unitysvc_data import applies_to

    assert applies_to("llm_connectivity") == {"capability": "chat", "upstream": "openai"}
    assert applies_to("llm_connectivity_anthropic") == {"capability": "chat", "upstream": "anthropic"}
    assert applies_to("llm_connectivity_embed") == {"capability": "embed"}
    assert applies_to("llm_connectivity_transcription") == {"capability": "speech-transcribe"}


def test_the_request_template_is_selected_like_everything_else():
    """`llm_request_template` is a chat-completion body, so it declares
    chat — rather than the collection special-casing chat to add it."""
    from unitysvc_data import applies_to

    assert applies_to("llm_request_template")["capability"] == "chat"
    assert applies_to("llm_request_template_anthropic")["upstream"] == "anthropic"


def test_the_how_to_doc_declares_nothing_because_it_is_universal():
    """An absent `capability` means "applies to every service" — which is
    how a universal document is expressed without a special case."""
    from unitysvc_data import applies_to

    assert applies_to("llm_description") == {}


def test_no_capability_is_hardcoded_in_the_selection_logic():
    """The guard against the chat special case creeping back."""
    import inspect

    from unitysvc_data import presets

    source = inspect.getsource(presets._select)
    assert '"chat"' not in source, "selection must not name a capability"


def test_two_matching_probes_do_not_collapse_onto_one_title():
    """A cohere embedding service matches both the OpenAI-compat probe and
    the Cohere-native image-embedding probe. Both are real and both should
    survive; a fixed per-category title silently dropped one."""
    docs = llm_example_collection({"capabilities": ["embed"], "formats": ["openai", "cohere"]})

    probes = [d for d in docs.values() if d["category"] == "connectivity_test"]
    assert len(probes) == 2
    assert {_key(p) for p in probes} == {
        _key(doc_preset("llm_connectivity_embed")),
        _key(doc_preset("llm_connectivity_embed_image")),
    }


def test_non_executable_documents_are_never_scoped_to_a_channel():
    """`meta.channels` / `meta.interfaces` tell the runner which channel to
    execute against. A markdown how-to and a JSON request template are
    never executed, so scoping them is meaningless — and on a multi-group
    service the value they got was simply whichever group happened to be
    processed last."""
    docs = llm_example_collection(BEDROCK)

    for title, record in docs.items():
        if record["category"] in ("code_example", "connectivity_test"):
            continue
        meta = record.get("meta") or {}
        assert "channels" not in meta, f"{title} ({record['category']}) was scoped"
        assert "interfaces" not in meta, f"{title} ({record['category']}) was scoped"


def test_scoping_a_document_does_not_depend_on_group_order():
    reversed_groups = {**BEDROCK, "formats": list(reversed(BEDROCK["formats"]))}

    a = llm_example_collection(BEDROCK)
    b = llm_example_collection(reversed_groups)

    assert {t: r.get("meta") for t, r in a.items()} == {t: r.get("meta") for t, r in b.items()}


def test_version_prefix_reaches_the_presets_that_declare_it():
    """cohere serves its OpenAI-compatible surface at /compatibility/v1 and
    crofai at /v2. Without threading this, every example points at /v1 and
    404s — 41 services silently mis-documented."""
    import pathlib

    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "params": {"version_prefix": "/compatibility/v1"}}
    )

    body = pathlib.Path(docs["cURL code example"]["file_path"]).read_text()
    assert "/compatibility/v1/chat/completions" in body
    assert "/v1/chat/completions" not in body.replace("/compatibility/v1/chat/completions", "")


def test_version_prefix_is_ignored_by_presets_that_declare_no_parameter():
    """`doc_preset` rejects an unknown kwarg as a bad metadata override, so
    the prefix must only be passed to presets that declare it."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "params": {"version_prefix": "/v2"}}
    )

    assert "How to use this model" in docs  # llm_description declares no parameters


def test_default_version_prefix_is_unchanged():
    import pathlib

    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    body = pathlib.Path(docs["cURL code example"]["file_path"]).read_text()
    assert "/v1/chat/completions" in body





def test_collection_level_params_broadcast_to_every_preset_declaring_them():
    """The broadcast form is not redundant with `example_params`: without
    it cohere would need an entry per preset, and a new example family
    would mean editing every repo — the drift this collection removes.

    Generic rather than a named `version_prefix=`, because llm presets
    already declare two parameters (version_prefix, language) and the
    package eight.
    """
    import pathlib

    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "params": {"version_prefix": "/v2"}}
    )

    body = pathlib.Path(docs["cURL code example"]["file_path"]).read_text()
    assert "/v2/chat/completions" in body


def test_broadcast_params_skip_presets_that_do_not_declare_them():
    """`llm_description` declares nothing, so a broadcast value must not
    reach it — doc_preset would reject it as a bad metadata override."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "params": {"version_prefix": "/v2"}}
    )

    assert "How to use this model" in docs


def test_a_broadcast_param_no_preset_declares_is_an_error():
    with pytest.raises(ValueError, match="nonsuch"):
        llm_example_collection(
            {"capabilities": ["chat"], "formats": ["openai"], "params": {"nonsuch": "x"}}
        )


def test_an_asserted_example_can_actually_produce_its_sentinel():
    """`output_contains` is checked against the example's stdout. A preset
    declaring a sentinel its body never prints would fail every run — a
    self-inflicted failure, not a real one."""
    import pathlib

    from unitysvc_data import MANIFEST, example_path

    broken = []
    for key, entry in MANIFEST["presets"].items():
        if not key.startswith("llm_") or entry["category"] != "code_example":
            continue
        needle = (entry.get("meta") or {}).get("output_contains")
        if not needle:
            continue
        body = pathlib.Path(example_path(entry["example_file"])).read_text()
        if needle not in body:
            broken.append(key)
    assert not broken, f"declare output_contains but never print it: {broken}"


def test_the_collection_takes_six_keys_and_no_more():
    """A guard on API surface. Anything a repo needs beyond these belongs
    in a sibling document, not a new option — see the tests below."""
    import inspect

    from unitysvc_data import presets

    source = inspect.getsource(presets.llm_example_collection)
    import re

    declared = set(re.findall(r'source\.get\("([a-z_]+)"\)', source))
    assert declared == {
        "capabilities",  # which capability to build a collection for
        "formats",       # caller dialects, plain list or scoped groups
        "upstream_dialect",
        "tools",         # gate for the function-calling example
        "sleep",         # meta.sleep_after_test, for rate-limited upstreams
        "params",        # broadcast to presets declaring the parameter
    }, f"API surface changed: {sorted(declared)}"


def test_a_sibling_document_adds_one_the_collection_cannot_derive():
    """The escape hatch is the sentinel's own sibling-merge, not a
    collection option: `expand_presets` merges sibling keys over the
    expanded mapping and expands their values first."""
    # unitysvc-data has zero runtime dependencies and unitysvc-core depends
    # on IT, not the reverse — so the merge itself is core's behaviour and
    # can only be documented here, where core happens to be installed.
    expand_presets = pytest.importorskip("unitysvc_core.utils").expand_presets

    out = expand_presets(
        {
            "$llm_example_collection": {"capabilities": ["chat"], "formats": ["openai"]},
            "Python code example (Cohere SDK)": {"$doc_preset": "llm_code_example_cohere"},
        }
    )

    assert "Python code example (Cohere SDK)" in out
    assert _key(out["Python code example (Cohere SDK)"]) == _key(doc_preset("llm_code_example_cohere"))


def test_a_sibling_overrides_a_generated_document_by_title():
    """Which is why the collection needs no per-example parameter option:
    restating the title replaces what it generated."""
    import pathlib

    expand_presets = pytest.importorskip("unitysvc_core.utils").expand_presets

    out = expand_presets(
        {
            "$llm_example_collection": {"capabilities": ["chat"], "formats": ["openai"]},
            "cURL code example": {
                "$doc_preset": {"name": "llm_code_example_shell", "version_prefix": "/v2"}
            },
        }
    )

    assert "/v2/chat/completions" in pathlib.Path(out["cURL code example"]["file_path"]).read_text()


def test_the_collection_returns_a_plain_mergeable_mapping():
    """The stdlib-only half of the sibling contract, so it is asserted even
    where unitysvc-core is not installed: the return value must be an
    ordinary dict keyed by title, so a caller can merge over it."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert type(docs) is dict
    assert all(isinstance(t, str) for t in docs)
    assert dict(docs, **{"cURL code example": {"replaced": True}})["cURL code example"] == {
        "replaced": True
    }
