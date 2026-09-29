"""Tests for ``llm_example_collection`` — the preset that expands a
service's (capability x format) declaration into a whole ``documents``
block, rather than a single document.

Records are compared against ``doc_preset(<name>)`` rather than by
inspecting ``file_path``: the collection must not invent its own record
shape, and ``llm_description`` resolves to a bundled path that does not
carry its preset name, so the path is not a usable key.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import jinja2
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


def _render_example(record: dict) -> str:
    source = Path(record["file_path"]).read_text()
    return jinja2.Environment(undefined=jinja2.ChainableUndefined).from_string(source).render()


def test_openai_native_examples_only_bound_output_tokens_when_requested():
    """The exceptional cap must not leak into copyable examples by default."""
    default_docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "tools": True}
    )
    capped_docs = llm_example_collection(
        {
            "capabilities": ["chat"],
            "formats": ["openai"],
            "tools": True,
            "params": {"max_tokens": "64"},
        }
    )

    for title, default_record in default_docs.items():
        if default_record["category"] != "code_example":
            continue
        assert "max_tokens" not in _render_example(default_record), title
        assert re.search(
            r'["\']?max_tokens["\']?\s*[:=]\s*64\b',
            _render_example(capped_docs[title]),
        ), title


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


def test_every_chat_upstream_gets_the_one_format_keyed_request_template():
    """v2 keys a body per request format, so an Anthropic upstream no longer
    needs its own template — and must not get both, which would collide on
    the title "Default request body"."""
    for upstream in ("openai", "anthropic"):
        docs = llm_example_collection(
            {"capabilities": ["chat"], "formats": ["anthropic"], "upstream_dialect": upstream}
        )
        templates = [d for d in docs.values() if d["category"] == "request_template"]
        assert len(templates) == 1
        assert "llm_request_template" in presets_in(docs)


def test_the_request_template_carries_a_body_for_each_request_format():
    body = json.loads(
        Path(doc_preset("llm_request_template")["file_path"]).read_text()
    )
    assert set(body) == {"openai", "anthropic", "cohere", "dashscope", "bedrock_converse"}
    # The gateway recognises each body as its own format by shape
    # (apisix-gateways request_meta.classify); keep the markers it keys on.
    assert "system" in body["anthropic"] and "max_tokens" in body["anthropic"]
    assert isinstance(body["dashscope"]["input"], dict)
    assert body["bedrock_converse"]["messages"][0]["content"] == [
        {"text": "Say hello in one sentence."}
    ]
    # No entry names a model: the routing key is merged in by the caller.
    assert all("model" not in entry for entry in body.values())


def test_the_pinned_v1_template_is_unchanged():
    v1 = json.loads(
        Path(doc_preset("llm_request_template_v1")["file_path"]).read_text()
    )
    assert set(v1) == {"max_tokens", "messages"}


def test_exactly_one_request_template_preset_serves_chat():
    """One keyed body, not one preset per format. A service accepting both
    OpenAI and Anthropic needs ONE default request body — the playground indexes
    it by the format the customer picked — and per-format presets would hand it
    two `Default request body` documents with no way to say which is the default.

    `llm_request_template_anthropic` was removed rather than kept unselected, so
    this asserts nothing has reintroduced a second one."""
    from unitysvc_data import PRESETS

    llm_templates = sorted(
        n for n in PRESETS if "request_template" in n and n.startswith("llm_")
    )
    # The family plus its version aliases, and nothing else.
    assert llm_templates == [
        "llm_request_template",
        "llm_request_template_v1",
        "llm_request_template_v2",
    ], llm_templates


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


def test_min_expected_metrics_defaults_to_bytes_out_on_every_executable_document():
    """Every executable document opts into billing verification (#1522) by
    default, on the one floor that's safe without knowing a provider's
    metering scheme: bytes_out is set by the gateway itself from the raw
    response size, unlike token counts which require a recognised dialect.

    Uses ``moderate`` (the guard examples), which declares no preset-own
    ``min_expected_metrics`` — see the union tests below for capabilities
    that layer a stronger, preset-specific floor on top."""
    docs = llm_example_collection({"capabilities": ["moderate"], "formats": ["openai"]})

    executable = [
        d for d in docs.values() if d["category"] in ("code_example", "connectivity_test")
    ]
    assert executable, "expected executable documents"
    assert all(d["meta"]["min_expected_metrics"] == {"bytes_out": 1} for d in executable)


def test_min_expected_metrics_default_does_not_clobber_the_presets_own_meta():
    docs = llm_example_collection({"capabilities": ["moderate"], "formats": ["openai"]})

    example = docs["Python code example (moderation, requests)"]
    assert example["meta"]["requirements"] == ["requests"]
    assert example["meta"]["min_expected_metrics"] == {"bytes_out": 1}


def test_min_expected_metrics_is_overridable_per_service():
    """A service that has verified its bundle does token-level metering can
    require a stricter floor than the byte-count default."""
    docs = llm_example_collection(
        {
            "capabilities": ["moderate"],
            "formats": ["openai"],
            "min_expected_metrics": {"output_tokens": 1},
        }
    )

    executable = [
        d for d in docs.values() if d["category"] in ("code_example", "connectivity_test")
    ]
    assert executable, "expected executable documents"
    assert all(d["meta"]["min_expected_metrics"] == {"output_tokens": 1} for d in executable)


def test_min_expected_metrics_empty_dict_opts_out():
    docs = llm_example_collection(
        {"capabilities": ["moderate"], "formats": ["openai"], "min_expected_metrics": {}}
    )

    executable = [
        d for d in docs.values() if d["category"] in ("code_example", "connectivity_test")
    ]
    assert executable, "expected executable documents"
    assert all("min_expected_metrics" not in d["meta"] for d in executable)


def test_min_expected_metrics_unions_with_the_presets_own_floor():
    """A preset that has verified its own dialect reports token counts
    (see the DeepSeek BYOK counter-example in unitysvc-data's CHANGELOG for
    why this is only declared per-preset, not defaulted platform-wide)
    layers its floor ON TOP of the collection's bytes_out default — both
    apply, the preset's floor doesn't replace the safety net."""
    docs = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    example = docs["Python code example (openai SDK)"]
    assert example["meta"]["requirements"] == ["openai"]
    assert example["meta"]["min_expected_metrics"] == {
        "bytes_out": 1,
        "input_tokens": 1,
        "output_tokens": 1,
    }

    probe = docs["Connectivity test"]
    assert probe["meta"]["min_expected_metrics"] == {
        "bytes_out": 1,
        "input_tokens": 1,
        "output_tokens": 1,
    }


def test_min_expected_metrics_preset_floor_wins_on_a_shared_key():
    """A collection-level override and a preset's own floor can name the
    same metric; the preset's own (more specific, verified) value wins."""
    docs = llm_example_collection(
        {
            "capabilities": ["chat"],
            "formats": ["openai"],
            "min_expected_metrics": {"input_tokens": 999},
        }
    )

    example = docs["Python code example (openai SDK)"]
    assert example["meta"]["min_expected_metrics"] == {"input_tokens": 1, "output_tokens": 1}


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


def test_every_declared_capability_contributes_its_examples():
    """A collection covers every capability the service declares. Dropping
    one would leave it undemonstrated while still declared — the exact
    failure this preset exists to prevent."""
    both = llm_example_collection(
        {"capabilities": ["chat", "image-text-to-text"], "formats": ["openai"]}
    )
    chat_only = llm_example_collection({"capabilities": ["chat"], "formats": ["openai"]})

    assert set(chat_only) < set(both)
    assert any("vision" in title for title in both)
    # Still one probe: liveness is a property of the service, not of a
    # capability, so fanning out must not duplicate it.
    assert len([d for d in both.values() if d["category"] == "connectivity_test"]) == 1


def test_fanning_out_capabilities_keeps_titles_distinct():
    """Titles key the ``documents`` mapping, so a chat example and an
    image-text-to-text example that rendered the same title would silently
    overwrite one another. The ``vision`` feature qualifier prevents it."""
    docs = llm_example_collection(
        {"capabilities": ["chat", "image-text-to-text"], "formats": ["openai", "anthropic"]}
    )

    assert len(docs) == len({_key(d) for d in docs.values()})


def test_declaring_an_undemonstrable_capability_still_raises():
    """The gate survives the fan-out: a capability with no code examples
    cannot be demonstrated, so it must not be declared."""
    with pytest.raises(ValueError, match="must not be declared"):
        llm_example_collection({"capabilities": ["chat", "telepathy"], "formats": ["openai"]})


def test_image_text_to_text_implies_the_vision_feature():
    """The capability needs the vision examples, so declaring it is enough
    — a listing does not have to set ``vision: true`` as well."""
    implied = llm_example_collection(
        {"capabilities": ["image-text-to-text"], "formats": ["openai"]}
    )
    explicit = llm_example_collection(
        {"capabilities": ["image-text-to-text"], "formats": [{"formats": ["openai"], "vision": True}]}
    )

    assert implied
    assert set(implied) == set(explicit)


def test_speech_transcribe_is_supported_since_its_presets_exist():
    """Found by the before/after sweep: three services (cohere-transcribe,
    groq whisper x2) were rejected even though unitysvc-data ships both
    the examples and the probe."""
    docs = llm_example_collection({"capabilities": ["speech-to-text"], "formats": ["openai"]})

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
    for capability in ("chat", "embed", "speech-to-text"):
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
    "speech-to-text": (
        {
            "llm_code_example_transcription_requests",
            "llm_code_example_transcription_javascript",
            "llm_code_example_transcription_shell",
        },
        "llm_connectivity_transcription",
    ),
    "text-to-speech": (
        {
            "llm_code_example_tts_requests",
            "llm_code_example_tts_javascript",
            "llm_code_example_tts_shell",
        },
        "llm_connectivity_tts",
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
        ("speech-to-text", "llm_connectivity_transcription"),
        ("text-to-speech", "llm_connectivity_tts"),
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
    assert applies_to("llm_connectivity_embed") == {
        "capability": "embed", "dialect": "openai"}
    assert applies_to("llm_connectivity_transcription") == {
        "capability": "speech-to-text", "dialect": "openai"}


def test_the_request_template_is_selected_like_everything_else():
    """`llm_request_template` is a chat-completion body, so it declares
    chat — rather than the collection special-casing chat to add it."""
    from unitysvc_data import applies_to

    assert applies_to("llm_request_template") == {"capability": "chat"}


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


def test_no_preset_emits_removed_output_contains_metadata():
    """Scripts own their assertions; the runner no longer matches stdout."""
    from unitysvc_data import MANIFEST

    offenders = [
        key
        for key, entry in MANIFEST["presets"].items()
        if "output_contains" in (entry.get("meta") or {})
    ]

    assert not offenders


def test_current_presets_do_not_print_retired_success_markers():
    """A literal success token can make an otherwise empty test look useful."""
    from unitysvc_data import MANIFEST

    examples_root = Path(__file__).parents[1] / "src" / "unitysvc_data" / "examples"
    exact_markers = {
        'echo "sent"',
        "echo 'sent'",
        'echo "ok"',
        "echo 'ok'",
        'print("ok")',
        "print('ok')",
    }
    offenders = []
    for target in sorted(set(MANIFEST["aliases"].values())):
        entry = MANIFEST["presets"][target]
        path = examples_root / entry["example_file"]
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            statement = line.strip()
            if not statement.startswith(("echo ", "print(")):
                continue
            magic_prefixes = (
                '"example ok',
                "'example ok",
                '"connectivity ok',
                "'connectivity ok",
            )
            if any(marker in statement for marker in magic_prefixes) or statement in exact_markers:
                offenders.append(f"{target}: {path.name}:{line_number}: {statement}")

    assert not offenders, "\n".join(offenders)


def test_the_collection_takes_seven_keys_and_no_more():
    """A guard on API surface. Anything a repo needs beyond these belongs
    in a sibling document, not a new option — see the tests below.

    ``min_expected_metrics`` earned first-class status (rather than the
    sibling escape hatch) on the same grounds as ``sleep``: it applies
    uniformly to every executable document the collection generates, and
    a per-title sibling override for something every document needs would
    mean reverse-engineering and repeating each preset's own record by
    hand (see unitysvc/unitysvc#1522's rollout for exactly that pain)."""
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
        "min_expected_metrics",  # meta.min_expected_metrics, billing-verification floor
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


# QwenCloud reaches us two ways at once: its compatibility layer speaks
# OpenAI, while its native DashScope API is the only surface serving TTS and
# ASR. Each is a separate channel on one service, so the upstream dialect
# differs BETWEEN groups of a single collection — unlike bedrock, where both
# groups front the same OpenAI-shaped upstream and only the caller's dialect
# differs.
QWENCLOUD = {
    "capabilities": ["chat"],
    "upstream_dialect": "openai",
    "formats": [
        {"formats": ["openai", "anthropic"], "channel": "managed",
         "interface": "canonical", "primary": True},
        {"formats": ["dashscope_text"], "channel": "dashscope-managed",
         "interface": "dashscope_api", "upstream_dialect": "dashscope"},
    ],
}


def test_a_group_may_override_the_collections_upstream_dialect():
    """A group maps to exactly one channel, and which dialect the upstream
    speaks is a property of that channel (`upstream_format` in its config) —
    not of the service. Without a per-group override, a collection can only
    describe channels that all front the same upstream dialect, so QwenCloud's
    native DashScope channel could not share a listing with its
    OpenAI-compatible one."""
    docs = llm_example_collection(QWENCLOUD)

    # The DashScope-native example is selected only because the group's own
    # upstream_dialect satisfied the preset's `upstream: dashscope`.
    native = docs["Python code example (DashScope input, requests)"]
    assert native["meta"]["channels"] == ["dashscope-managed"]
    assert native["meta"]["interfaces"] == ["dashscope_api"]

    # ...and the compat group still gets the OpenAI-upstream examples, which
    # the DashScope presets must not displace.
    assert "llm_code_example_requests" in examples_in(docs)


def test_an_unscoped_collection_still_uses_one_upstream_dialect():
    """The override is opt-in per group: a collection that declares only
    `upstream_dialect` keeps selecting against it for every group, so no
    existing repo changes behaviour."""
    docs = llm_example_collection(
        {"capabilities": ["chat"], "formats": ["openai"], "upstream_dialect": "dashscope"}
    )

    assert "llm_code_example_chat_dashscope_requests" not in examples_in(docs)


def test_a_group_may_scope_to_several_channels():
    """`channel` names one, which is all bedrock needs — each of its interfaces
    fronts a single channel. An interface with BOTH a managed and a byok channel
    needs to name both: scoping to one leaves the other undocumented, and
    scoping to neither fans every document across every channel, including the
    channels of the OTHER interface, where its dialect is wrong."""
    docs = llm_example_collection({
        "capabilities": ["chat"],
        "formats": [
            {"formats": ["openai"], "channels": ["managed", "byok"],
             "interface": "canonical", "primary": True},
            {"formats": ["dashscope_text"], "channels": ["ds-managed", "ds-byok"],
             "interface": "dashscope", "upstream_dialect": "dashscope"},
        ],
    })

    compat = docs["Python code example (requests)"]
    assert compat["meta"]["channels"] == ["managed", "byok"]
    assert compat["meta"]["interfaces"] == ["canonical"]

    native = docs["Python code example (DashScope input, requests)"]
    assert native["meta"]["channels"] == ["ds-managed", "ds-byok"]
    assert native["meta"]["interfaces"] == ["dashscope"]


def test_the_singular_channel_key_still_works():
    """bedrock's form is unchanged."""
    docs = llm_example_collection(BEDROCK)

    assert docs["Python code example (boto3 Converse)"]["meta"]["channels"] == ["converse"]


def test_a_modality_example_is_scoped_to_the_dialect_it_is_written_in():
    """Every stock modality example targets an OpenAI path — /audio/speech,
    /embeddings, /images/generations, /rerank — so each is an OpenAI-dialect
    document and must say so. They used to constrain only `capability`, which
    made them apply to EVERY dialect: a DashScope-only TTS service picked up the
    /v1/audio/speech example, an endpoint QwenCloud answers with 404."""
    native = llm_example_collection({
        "capabilities": ["text-to-speech"],
        "formats": [{"formats": ["dashscope_multimodal"], "interface": "dashscope",
                     "upstream_dialect": "dashscope"}],
    })
    assert "llm_code_example_tts_requests" not in examples_in(native)
    # The multimodal token selects the OMNI shape; the dedicated-model shape
    # lives under `dashscope_audio_task` (0.2.6).
    assert "llm_code_example_omni_tts_dashscope_requests" in examples_in(native)

    # ...and the OpenAI-dialect service that always had them still does.
    compat = llm_example_collection(
        {"capabilities": ["text-to-speech"], "formats": ["openai"]}
    )
    assert "llm_code_example_tts_requests" in examples_in(compat)


def test_every_capability_example_is_pinned_to_a_wire_shape():
    """The gap this closes, as an invariant. A document that names its capability
    and nothing else applies to EVERY dialect and every upstream, so it is served
    to a caller writing a wire shape it was not written in — which is how a
    DashScope-only TTS service came to publish an /v1/audio/speech example.

    Either constraint closes it, because either one excludes a native group:
    `dialect` pins what the CALLER writes, `upstream` what the upstream speaks,
    and a DashScope channel differs on both. `llm_description` is the deliberate
    exception — it constrains nothing because it really does apply to everything.

    `llm_request_template` is the other one: from v2 it carries a body for EVERY
    request format, keyed by format name, and the playground picks the entry for
    the format the caller writes. It is pinned to a wire shape per entry rather
    than per document.
    """
    from unitysvc_data import MANIFEST
    from unitysvc_data.presets import applies_to

    keyed_by_format = {"llm_request_template"}
    names = {r.get("preset_name", k) for k, r in MANIFEST["presets"].items()
             if k.startswith("llm_")}
    gaps = sorted(n for n in names
                  if (a := applies_to(n)).get("capability")
                  and not a.get("dialect") and not a.get("upstream")
                  and n not in keyed_by_format)
    assert gaps == [], f"these name a capability but no wire shape: {gaps}"


def test_a_multi_capability_service_keeps_every_capability_s_examples():
    """`docs` is keyed by title, and the title carried the dialect, the feature
    and the SDK but never the CAPABILITY. So for a service declaring several,
    two documents that differ only by capability produced the same title and one
    silently overwrote the other — an omni model declaring chat, text-to-speech
    and speech-to-text shipped ONE of those three sets of examples."""
    docs = llm_example_collection({
        "capabilities": ["chat", "text-to-speech", "speech-to-text"],
        "formats": [{"formats": ["dashscope_multimodal"], "interface": "dashscope",
                     "upstream_dialect": "dashscope"}],
    })
    names = examples_in(docs)
    for expected in ("llm_code_example_chat_dashscope_requests",
                     "llm_code_example_omni_tts_dashscope_requests",
                     "llm_code_example_omni_asr_dashscope_requests"):
        assert expected in names, f"{expected} was overwritten by a sibling"
    # ...and each probe survives too.
    probes = [d for d in docs.values() if d["category"] == "connectivity_test"]
    assert len(probes) == 3, f"expected one probe per capability, got {len(probes)}"


def test_a_title_names_its_capability_unconditionally():
    """Not only when a sibling capability would collide with it. The rule has to
    hold for one service in isolation, because whether a title is unique cannot
    depend on what else the service happens to declare."""
    docs = llm_example_collection({"capabilities": ["embed"], "formats": ["openai"]})

    assert "Python code example (embeddings, requests)" in docs
    assert "Connectivity test (embeddings)" in docs


def test_chat_and_vision_titles_carry_no_capability_label():
    """The two deliberate exceptions. Chat is the reading a bare title already
    has, and vision is carried by the `vision` feature bit — so neither can
    collide with a labelled sibling, and labelling them would churn the titles of
    nearly every published service. A title is a document's key."""
    docs = llm_example_collection(
        {"capabilities": ["chat", "image-text-to-text"], "formats": ["openai"]}
    )

    assert "Python code example (requests)" in docs, "chat stays unlabelled"
    assert any("vision" in t for t in docs), "vision is named by its feature bit"
    assert not any("image-text-to-text" in t for t in docs)


def test_omni_audio_examples_are_chat_shaped_and_stream_for_output():
    """An omni model reaches speech as a CHAT call: `input.messages` plus
    `parameters.modalities`. It rejects the dedicated-model `input.text` request
    with `Either "prompt" or "messages" must exist`, so the two shapes cannot
    share a dialect token — and they did, which meant one silently overwrote the
    other for the same capability."""
    import pathlib

    docs = llm_example_collection({
        "capabilities": ["chat", "text-to-speech", "speech-to-text"],
        "formats": [{"formats": ["dashscope_multimodal"], "interface": "dashscope",
                     "upstream_dialect": "dashscope"}],
    })
    audio = {t: d for t, d in docs.items()
             if "speech" in t or "transcription" in t}
    assert len(audio) == 8, f"expected 4 speech + 4 transcription, got {sorted(audio)}"

    for title, doc in audio.items():
        body = pathlib.Path(doc["file_path"]).read_text()
        assert "messages" in body, f"{title} must send input.messages"
        # Audio OUTPUT is streaming-only: without the SSE header the call still
        # returns 200 and still bills audio tokens, and carries no audio at all.
        if "speech" in title:
            assert "X-DashScope-SSE" in body, f"{title} must stream"
            assert "modalities" in body, f"{title} must ask for audio output"
        else:
            assert "X-DashScope-SSE" not in body, f"{title} needs no stream"


def test_the_dedicated_audio_shape_has_its_own_dialect():
    """A single-purpose TTS/ASR model takes `input.text` / `input.audio` with no
    messages at all. Same capability, different wire shape, so a different token
    — otherwise both match and the collection keeps only one."""
    from unitysvc_data.presets import applies_to

    assert applies_to("llm_code_example_tts_dashscope_requests")["dialect"] == (
        "dashscope_audio_task")
    assert applies_to("llm_code_example_omni_tts_dashscope_requests")["dialect"] == (
        "dashscope_multimodal")

    # ...and an omni group selects only the omni ones.
    docs = llm_example_collection({
        "capabilities": ["text-to-speech"],
        "formats": [{"formats": ["dashscope_multimodal"], "interface": "dashscope",
                     "upstream_dialect": "dashscope"}],
    })
    names = examples_in(docs)
    assert "llm_code_example_omni_tts_dashscope_requests" in names
    assert "llm_code_example_tts_dashscope_requests" not in names


def test_omni_audio_floors_are_tokens_not_characters():
    """Probed: omni audio bills in tokens, with the audio counted in
    `output_tokens_details.audio_tokens`. A `characters` floor there fails
    verification on a service that meters correctly."""
    docs = llm_example_collection({
        "capabilities": ["text-to-speech", "speech-to-text"],
        "formats": [{"formats": ["dashscope_multimodal"], "interface": "dashscope",
                     "upstream_dialect": "dashscope"}],
    })
    for title, doc in docs.items():
        floor = (doc.get("meta") or {}).get("min_expected_metrics")
        if floor is not None:
            assert "characters" not in floor, f"{title} still demands characters"


def test_a_group_may_serve_a_subset_of_the_service_s_capabilities():
    """`capabilities` fans across every group, so a group advertises the service's
    whole capability list whether or not its endpoint serves them. QwenCloud's
    compatible-mode endpoint serves chat and embeddings but answers
    `/v1/audio/speech` and `/v1/audio/transcriptions` with 404 — yet an omni
    service's compat group pulled in the stock OpenAI audio examples and failed
    them, while its native group handled audio correctly."""
    docs = llm_example_collection({
        "capabilities": ["chat", "text-to-speech"],
        "formats": [
            # The compat endpoint serves chat only; say so.
            {"formats": ["openai"], "capabilities": ["chat"],
             "interface": "canonical", "primary": True},
            {"formats": ["dashscope_multimodal"], "interface": "dashscope",
             "upstream_dialect": "dashscope"},
        ],
    })
    names = examples_in(docs)
    # The stock /v1/audio/speech example must NOT be selected...
    assert "llm_code_example_tts_requests" not in names
    # ...while the native one is, and chat still reaches the compat endpoint.
    assert "llm_code_example_omni_tts_dashscope_requests" in names
    assert "llm_code_example_requests" in names


def test_a_group_without_capabilities_still_serves_all_of_them():
    """Opt-in per group: every existing repo declares none and is unaffected."""
    docs = llm_example_collection({
        "capabilities": ["chat", "text-to-speech"],
        "formats": [{"formats": ["openai"], "interface": "canonical"}],
    })
    names = examples_in(docs)
    assert "llm_code_example_requests" in names
    assert "llm_code_example_tts_requests" in names


def test_the_omni_tts_probe_never_pipes_its_response():
    """Its stream is ~140 KB of base64 audio, far past the pipe buffer. A reader
    that stops early — `head -c 200`, or `grep -q` on its first match — closes
    the pipe, the writer takes SIGPIPE, and under `pipefail` the probe exits 141
    with a request that actually succeeded. Staging rejected a service for
    exactly that.

    Reproduced at 213 KB: the piped form exits 141, the substring form exits 0.
    """
    import pathlib

    body = pathlib.Path(
        doc_preset("llm_connectivity_omni_tts_dashscope")["file_path"]
    ).read_text()
    offenders = [
        line.strip() for line in body.splitlines()
        if '"$response"' in line and "|" in line
    ]
    assert not offenders, f"pipes the response: {offenders}"
    # ...and it still checks for audio, by reading the variable directly.
    assert 'case "$response" in' in body
    assert '"audio"' in body
