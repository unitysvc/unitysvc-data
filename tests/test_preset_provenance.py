"""Preset output must be reproducible from serialized document metadata alone."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from unitysvc_data import (
    ALIASES,
    MANIFEST,
    PRESET_FNS,
    PRESETS,
    __version__,
    doc_preset,
    llm_example_collection,
    regenerate_document,
    register_jinja_globals,
)


def _with_content(document):
    """Installation and temporary paths are not part of the document identity."""
    return {
        **{key: value for key, value in document.items() if key != "file_path"},
        "file_content": Path(document["file_path"]).read_text(encoding="utf-8"),
    }


@pytest.mark.parametrize("name", sorted(MANIFEST["presets"]))
def test_every_versioned_document_round_trips_from_json_metadata(name):
    original = doc_preset(name)
    meta = json.loads(json.dumps(original["meta"]))
    assert _with_content(regenerate_document(meta)) == _with_content(original)


def test_recipe_records_canonical_name_defaults_and_effective_overrides():
    document = doc_preset(
        "llm_code_example_openai",
        description="Our API",
        is_active=False,
        is_public=False,
        version_prefix="/compatibility/v1",
        meta={"timeout": 90, "channels": ["managed", "byok"]},
    )
    recipe = document["meta"]["preset"]
    assert recipe["name"] == ALIASES["llm_code_example_openai"]
    assert recipe["data_version"] == __version__
    assert recipe["parameters"]["version_prefix"] == "/compatibility/v1"
    declared = MANIFEST["presets"][recipe["name"]]["parameters"]
    assert recipe["parameters"] == {**declared, "version_prefix": "/compatibility/v1"}
    assert recipe["overrides"]["description"] == "Our API"
    assert recipe["overrides"]["is_active"] is False
    assert recipe["overrides"]["is_public"] is False
    assert recipe["overrides"]["meta"] == {key: value for key, value in document["meta"].items() if key != "preset"}
    assert _with_content(regenerate_document(json.loads(json.dumps(document["meta"])))) == _with_content(document)


def test_regeneration_ignores_later_alias_changes(monkeypatch):
    document = doc_preset("s3_connectivity")
    monkeypatch.setitem(ALIASES, "s3_connectivity", "smtp_connectivity_v1")
    assert _with_content(regenerate_document(document["meta"])) == _with_content(document)


@pytest.mark.parametrize(
    "source",
    [
        {"capabilities": ["chat"], "formats": ["openai"]},
        {
            "capabilities": ["chat", "embed"],
            "formats": [
                {
                    "formats": ["openai", "anthropic"],
                    "channels": ["managed", "byok"],
                    "interface": "canonical",
                    "primary": True,
                    "test_status": "skip",
                    "params": {"version_prefix": "/compatibility/v1"},
                },
                {"formats": ["cohere"], "channel": "cohere", "interface": "cohere"},
            ],
            "tools": True,
            "sleep": 2,
            "params": {"max_tokens": "64"},
            "min_expected_metrics": {"bytes_out": 2},
        },
    ],
)
def test_bundle_documents_regenerate_individually_with_their_final_scope(source):
    documents = llm_example_collection(source)
    assert len(documents) > 1
    for title, document in documents.items():
        meta = json.loads(json.dumps(document["meta"]))
        assert meta["preset"]["name"] in MANIFEST["presets"], title
        assert _with_content(regenerate_document(meta)) == _with_content(document), title


def test_regeneration_in_another_process_needs_no_original_materialized_file(tmp_path):
    document = doc_preset("llm_code_example_openai", version_prefix="/custom/v2")
    expected = _with_content(document)
    original_path = Path(document["file_path"])
    original_path.unlink()
    payload = json.dumps(document["meta"])
    assert str(original_path) not in payload
    process = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; from pathlib import Path; from unitysvc_data import regenerate_document; "
                "doc = regenerate_document(json.load(sys.stdin)); "
                "doc['file_content'] = Path(doc.pop('file_path')).read_text(encoding='utf-8'); "
                "print(json.dumps(doc))"
            ),
        ],
        input=payload,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(process.stdout) == expected


def test_registry_and_jinja_factories_produce_the_same_reproducible_document():
    jinja2 = pytest.importorskip("jinja2")
    env = jinja2.Environment()
    register_jinja_globals(env)
    name = "llm_code_example_openai"
    direct = doc_preset(name, version_prefix="/v2")
    factory = PRESETS[name](version_prefix="/v2")
    sentinel = PRESET_FNS["doc_preset"]({"name": name, "version_prefix": "/v2"})
    rendered = json.loads(env.from_string("{{ llm_code_example_openai(version_prefix='/v2') | tojson }}").render())
    assert direct == factory == sentinel == rendered
    assert _with_content(regenerate_document(rendered["meta"])) == _with_content(direct)


@pytest.mark.parametrize("value", [{}, {"name": "s3_connectivity_v1"}, None, False])
def test_callers_cannot_override_reserved_provenance(value):
    with pytest.raises(ValueError, match=r"meta\.preset is reserved"):
        doc_preset("s3_connectivity", meta={"preset": value})
    with pytest.raises(ValueError, match=r"meta\.preset is reserved"):
        PRESETS["s3_connectivity"](meta={"preset": value})


def test_metadata_and_caller_overrides_are_independent_copies():
    overrides = {"channels": ["managed"]}
    original = doc_preset("s3_connectivity", meta=overrides)
    saved = deepcopy(original)
    overrides["channels"].append("byok")
    assert original == saved
    regenerated = regenerate_document(original["meta"])
    regenerated["meta"]["preset"]["overrides"]["meta"]["channels"].append("other")
    assert original == saved
    original["meta"]["channels"].append("changed")
    assert original["meta"]["preset"]["overrides"]["meta"]["channels"] == ["managed"]


@pytest.mark.parametrize("meta", [None, [], {}, {"preset": "s3_connectivity_v1"}, {"preset": {}}])
def test_missing_or_malformed_recipe_is_rejected(meta):
    with pytest.raises(ValueError, match=r"meta\.preset must be an object"):
        regenerate_document(meta)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("data_version", "0.0.0", "Regeneration requires unitysvc-data"),
        ("name", "s3_connectivity", "known versioned preset"),
        ("name", "unknown_v1", "known versioned preset"),
        ("name", [], "known versioned preset"),
        ("parameters", {"unknown": "value"}, "resolved string parameters"),
        ("parameters", [], "resolved string parameters"),
        ("overrides", {"file_path": "/tmp/custom.py"}, "overrides must contain exactly"),
    ],
)
def test_incompatible_or_invalid_recipe_is_rejected(field, value, message):
    meta = doc_preset("s3_connectivity")["meta"]
    meta["preset"][field] = value
    with pytest.raises(ValueError, match=message):
        regenerate_document(meta)


def test_recipe_requires_all_resolved_parameters_and_string_values():
    meta = doc_preset("llm_code_example_openai")["meta"]
    for parameters in ({}, {**meta["preset"]["parameters"], "version_prefix": 2}):
        altered = deepcopy(meta)
        altered["preset"]["parameters"] = parameters
        with pytest.raises(ValueError, match="resolved string parameters"):
            regenerate_document(altered)


def test_nested_provenance_cannot_be_replayed_as_an_override():
    meta = doc_preset("s3_connectivity")["meta"]
    meta["preset"]["overrides"]["meta"]["preset"] = {}
    with pytest.raises(ValueError, match=r"meta\.preset is reserved"):
        regenerate_document(meta)
