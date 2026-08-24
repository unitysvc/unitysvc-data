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


def test_unknown_capability_is_an_error_not_a_silent_chat_fallback():
    """A capability with no probe must fail loudly. Six services today
    declare rerank / speech-synthesize / moderate with no matching
    connectivity preset; silently handing them a chat probe is how that
    went unnoticed."""
    with pytest.raises(ValueError, match="rerank"):
        llm_example_collection({"capabilities": ["rerank"], "formats": ["openai"]})


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
