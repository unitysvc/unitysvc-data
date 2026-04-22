"""Tests for doc_preset, file_preset, aliases, and manifest freshness."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from unitysvc_data import (
    ALIASES,
    MANIFEST,
    PRESETS,
    doc_preset,
    example_path,
    file_preset,
    list_examples,
    list_presets,
    read_example,
    register_jinja_globals,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Manifest shape and integrity
# ---------------------------------------------------------------------------


def test_manifest_has_presets_and_aliases():
    assert MANIFEST["version"] == "1"
    assert MANIFEST["presets"], "expected at least one preset"
    assert MANIFEST["aliases"], "expected at least one alias"


def test_every_preset_points_at_an_existing_file():
    for name, entry in MANIFEST["presets"].items():
        rel = entry["example_file"]
        path = example_path(rel)
        assert path.is_file(), f"{name}: file {rel} missing"
        assert path.is_absolute()


def test_every_alias_resolves_to_a_concrete_preset():
    for alias, target in ALIASES.items():
        assert target in MANIFEST["presets"], f"alias {alias!r} points at missing {target!r}"
        assert MANIFEST["presets"][target]["preset_name"] == alias, (
            f"alias {alias!r} should match preset_name of target {target!r}"
        )


def test_alias_targets_latest_version():
    from collections import defaultdict

    families: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for name, entry in MANIFEST["presets"].items():
        families[entry["preset_name"]].append((entry["version"], name))

    for preset_name, versions in families.items():
        versions.sort()
        latest = versions[-1][1]
        assert ALIASES.get(preset_name) == latest, (
            f"alias {preset_name!r} should point at {latest!r}, got {ALIASES.get(preset_name)!r}"
        )


# ---------------------------------------------------------------------------
# PRESETS registry and file discovery
# ---------------------------------------------------------------------------


def test_presets_contains_both_versioned_and_aliases():
    for name in MANIFEST["presets"]:
        assert name in PRESETS, f"versioned preset {name!r} missing from PRESETS"
    for alias in ALIASES:
        assert alias in PRESETS, f"alias {alias!r} missing from PRESETS"


def test_list_presets_returns_versioned_and_aliases():
    versioned, aliases = list_presets()
    assert versioned == sorted(MANIFEST["presets"])
    assert aliases == ALIASES
    # The tuple items are independent copies — mutating shouldn't
    # corrupt package state.
    aliases.clear()
    assert ALIASES, "list_presets aliases dict should be an independent copy"


def test_list_examples_excludes_readmes_and_dotfiles():
    names = list_examples()
    assert names
    assert all(not n.endswith("README.md") for n in names)
    assert all(not n.startswith(".") and "/." not in n for n in names)


def test_example_path_roundtrips_with_read_example():
    any_name = list_examples()[0]
    path = example_path(any_name)
    assert path.is_file()
    assert read_example(any_name) == path.read_text(encoding="utf-8")


def test_example_path_raises_for_unknown():
    with pytest.raises(FileNotFoundError):
        example_path("does-not-exist.sh")


# ---------------------------------------------------------------------------
# doc_preset — sentinel form
# ---------------------------------------------------------------------------


def test_doc_preset_sentinel_versioned():
    record = doc_preset({"$preset": "s3_connectivity_v1"})
    assert record["category"] == "connectivity_test"
    assert record["mime_type"] == "python"
    assert record["meta"] == {"output_contains": "connectivity ok"}
    assert Path(record["file_path"]).is_file()


def test_doc_preset_alias_equals_latest_version():
    alias_record = doc_preset({"$preset": "s3_connectivity"})
    versioned_record = doc_preset({"$preset": "s3_connectivity_v1"})
    assert alias_record == versioned_record


def test_doc_preset_sentinel_with_overrides():
    record = doc_preset(
        {
            "$preset": "s3_code_example",
            "$with": {"description": "Custom desc", "is_public": False},
        }
    )
    assert record["description"] == "Custom desc"
    assert record["is_public"] is False
    assert record["category"] == "code_example"


def test_doc_preset_deep_merges_meta():
    record = doc_preset(
        {"$preset": "smtp_connectivity_v1", "$with": {"meta": {"timeout_s": 10}}}
    )
    assert record["meta"] == {"output_contains": "connectivity ok", "timeout_s": 10}


def test_doc_preset_returns_fresh_copy():
    a = doc_preset({"$preset": "s3_connectivity_v1"})
    b = doc_preset({"$preset": "s3_connectivity_v1"})
    a["description"] = "mutated"
    assert b["description"] != "mutated"


# ---------------------------------------------------------------------------
# doc_preset — bare-name form
# ---------------------------------------------------------------------------


def test_doc_preset_bare_name():
    record = doc_preset("s3_connectivity_v1")
    assert record["mime_type"] == "python"


def test_doc_preset_bare_name_with_kwarg_overrides():
    record = doc_preset("s3_code_example_v1", description="Custom", is_public=False)
    assert record["description"] == "Custom"
    assert record["is_public"] is False


def test_doc_preset_bare_name_and_sentinel_agree():
    bare = doc_preset("s3_connectivity", description="X")
    sentinel = doc_preset({"$preset": "s3_connectivity", "$with": {"description": "X"}})
    assert bare == sentinel


# ---------------------------------------------------------------------------
# doc_preset — error paths
# ---------------------------------------------------------------------------


def test_doc_preset_rejects_forbidden_overrides():
    with pytest.raises(ValueError, match="Cannot override"):
        doc_preset({"$preset": "s3_connectivity_v1", "$with": {"category": "other"}})
    with pytest.raises(ValueError, match="Cannot override"):
        doc_preset("s3_connectivity_v1", mime_type="other")


def test_doc_preset_rejects_unknown_name():
    with pytest.raises(KeyError, match="Unknown preset"):
        doc_preset("no_such_preset_v1")
    with pytest.raises(KeyError, match="Unknown preset"):
        doc_preset({"$preset": "no_such_preset_v1"})


def test_doc_preset_rejects_unknown_sentinel_keys():
    with pytest.raises(ValueError, match="Unknown keys"):
        doc_preset({"$preset": "s3_connectivity_v1", "weird": True})


def test_doc_preset_rejects_non_sentinel_dict():
    with pytest.raises(ValueError, match="missing '\\$preset'"):
        doc_preset({"category": "foo"})


def test_doc_preset_rejects_bad_source_type():
    with pytest.raises(TypeError, match="Expected a preset name string or"):
        doc_preset(42)


def test_doc_preset_rejects_bad_sentinel_types():
    with pytest.raises(ValueError, match="must be a string"):
        doc_preset({"$preset": 42})
    with pytest.raises(ValueError, match="must be an object"):
        doc_preset({"$preset": "s3_connectivity_v1", "$with": "oops"})


def test_doc_preset_rejects_mixed_overrides():
    with pytest.raises(ValueError, match="Cannot combine keyword overrides"):
        doc_preset(
            {"$preset": "s3_connectivity_v1", "$with": {"description": "a"}},
            description="b",
        )


# ---------------------------------------------------------------------------
# file_preset
# ---------------------------------------------------------------------------


def test_file_preset_bare_name_returns_content():
    content = file_preset("s3_connectivity_v1")
    assert isinstance(content, str)
    assert content  # non-empty
    # The s3 connectivity script has a recognisable signature.
    assert "boto3" in content


def test_file_preset_sentinel_returns_same_content():
    bare = file_preset("s3_connectivity_v1")
    sentinel = file_preset({"$preset": "s3_connectivity_v1"})
    assert bare == sentinel


def test_file_preset_alias_equals_latest_version():
    alias_content = file_preset("s3_connectivity")
    versioned_content = file_preset("s3_connectivity_v1")
    assert alias_content == versioned_content


def test_file_preset_matches_doc_preset_file_path():
    record = doc_preset("s3_connectivity_v1")
    expected = Path(record["file_path"]).read_text(encoding="utf-8")
    assert file_preset("s3_connectivity_v1") == expected


def test_file_preset_rejects_with_block():
    with pytest.raises(ValueError, match="does not support '\\$with'"):
        file_preset({"$preset": "s3_connectivity_v1", "$with": {"description": "x"}})


def test_file_preset_rejects_unknown_name():
    with pytest.raises(KeyError, match="Unknown preset"):
        file_preset("no_such_preset_v1")


def test_file_preset_rejects_bad_source_type():
    with pytest.raises(TypeError, match="Expected a preset name string or"):
        file_preset(None)


# ---------------------------------------------------------------------------
# Jinja globals
# ---------------------------------------------------------------------------


def test_register_jinja_globals_exposes_factories_and_aliases():
    pytest.importorskip("jinja2")
    from jinja2 import Environment

    env = Environment()
    register_jinja_globals(env)

    for name in PRESETS:
        assert callable(env.globals[name])

    record_direct = PRESETS["s3_connectivity"]()
    rendered = env.from_string("{{ s3_connectivity() | tojson }}").render()
    import json as _json

    assert _json.loads(rendered) == record_direct


# ---------------------------------------------------------------------------
# Manifest freshness
# ---------------------------------------------------------------------------


def test_manifest_is_up_to_date():
    """Run `tools/build.py --check` and assert it exits zero."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "build.py"), "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"tools/build.py --check failed:\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
