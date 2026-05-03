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
    assert record["meta"] == {"output_contains": "connectivity ok", "requirements": ["boto3"]}
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
    with pytest.raises(ValueError, match="Cannot combine keyword arguments"):
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
    with pytest.raises(ValueError, match="does not support metadata overrides"):
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


# ---------------------------------------------------------------------------
# @preset decorator + PRESET_FNS registry
# ---------------------------------------------------------------------------


def test_preset_fns_registry_contains_doc_and_file():
    from unitysvc_data import PRESET_FNS

    assert "doc_preset" in PRESET_FNS
    assert "file_preset" in PRESET_FNS
    # Each registered entry is callable.
    assert callable(PRESET_FNS["doc_preset"])
    assert callable(PRESET_FNS["file_preset"])


def test_preset_decorator_unpacks_flat_form():
    """The wrapper auto-unpacks {"name": "<x>", ...} into fn("<x>", **rest)."""
    from unitysvc_data import PRESET_FNS

    # Flat form via the registered wrapper should equal direct call.
    via_registry = PRESET_FNS["doc_preset"](
        {"name": "s3_connectivity_v1", "is_public": True}
    )
    via_direct = doc_preset("s3_connectivity_v1", is_public=True)
    assert via_registry == via_direct


def test_preset_decorator_forwards_bare_string():
    from unitysvc_data import PRESET_FNS

    via_registry = PRESET_FNS["doc_preset"]("s3_connectivity_v1")
    via_direct = doc_preset("s3_connectivity_v1")
    assert via_registry == via_direct


def test_preset_decorator_preserves_original_function_signature():
    """@preset returns the undecorated function so programmatic callers
    keep the original signature (`**overrides`, etc.)."""
    import inspect

    sig = inspect.signature(doc_preset)
    # If @preset had replaced doc_preset with the single-arg wrapper,
    # we would see just `source` here.
    assert "overrides" in sig.parameters or any(
        p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
    )


def test_preset_decorator_does_not_duplicate_across_reimports():
    """Re-importing the module must not double-register any preset."""
    import importlib

    import unitysvc_data._registry as reg

    before = dict(reg.PRESET_FNS)
    importlib.reload(reg)
    # After reload, each preset appears at most once in the new registry.
    # (We can't easily re-decorate here without re-running presets.py, but
    # we can at least confirm the registry isn't "leaking" entries.)
    assert set(reg.PRESET_FNS) <= set(before) | {"doc_preset", "file_preset"}


def test_preset_decorator_register_custom_function():
    """Third-party code can register a new sentinel type with @preset."""
    from unitysvc_data._registry import PRESET_FNS, preset

    try:
        @preset
        def _custom_preset(source, **kwargs):
            return {"source": source, "kwargs": kwargs}

        assert "_custom_preset" in PRESET_FNS
        assert PRESET_FNS["_custom_preset"]({"name": "x", "flag": True}) == {
            "source": "x",
            "kwargs": {"flag": True},
        }
    finally:
        PRESET_FNS.pop("_custom_preset", None)


# ---------------------------------------------------------------------------
# Preset parameters — ${__name__} substitution at file_preset time
# ---------------------------------------------------------------------------


def test_existing_presets_with_param_refs_at_least_render_cleanly():
    """Smoke test: every preset that has ``${__name__}`` in its body
    successfully passes through ``file_preset`` with defaults.  Names
    not declared in the family's parameters table render as their
    literal source (best-effort substitution), which is fine."""
    import re

    pat = re.compile(r"\$\{__([A-Za-z_][A-Za-z0-9_]*)__\}")
    for name, entry in MANIFEST["presets"].items():
        body = example_path(entry["example_file"]).read_text(encoding="utf-8")
        if not pat.search(body):
            continue
        # Default render must not raise.
        rendered = file_preset(name)
        # Any declared name must have been substituted (no literal left).
        for declared_name in entry.get("parameters", {}):
            assert "${__" + declared_name + "__}" not in rendered, (
                f"{name}: declared parameter {declared_name!r} not substituted"
            )


def test_file_preset_no_parameters_returns_unchanged():
    """Existing parameter-free presets pass through file content
    untouched — fast path, no regex sub."""
    raw = example_path(MANIFEST["presets"]["s3_connectivity_v1"]["example_file"]).read_text(
        encoding="utf-8"
    )
    assert file_preset("s3_connectivity_v1") == raw


def test_file_preset_rejects_unknown_param_kwarg():
    with pytest.raises(ValueError, match="Unknown parameter"):
        file_preset("s3_connectivity_v1", version_prefix="/x")


def test_file_preset_rejects_non_string_param_kwarg():
    with pytest.raises(ValueError, match="must be a string"):
        # Use any preset; param value validation runs before declared-name
        # check, so it doesn't matter that this preset has no parameters.
        file_preset("s3_connectivity_v1", anything=123)


def test_doc_preset_carries_no_params_field_when_unused():
    """Existing presets get no ``_params`` key on the doc record — the
    field is only added when params are actually supplied."""
    record = doc_preset("s3_connectivity_v1")
    assert "_params" not in record


# ---------------------------------------------------------------------------
# Flat-form auto-discrimination — the seller-facing public API
# ---------------------------------------------------------------------------


def test_doc_preset_flat_form_auto_discriminates_overrides_only(monkeypatch):
    """Synthesize a preset with declared parameters, then verify the
    flat form correctly sends overrides to the factory and parameters
    to the record's ``_params`` field."""
    from unitysvc_data import presets as p

    # Inject a synthetic declaration on an existing preset so we don't
    # have to author a whole new family for the test.
    target = "s3_code_example_v1"
    monkeypatch.setitem(p._PRESET_PARAMETERS, target, {"version_prefix": "/v1"})

    record = doc_preset(target, description="Custom", version_prefix="/v2")
    assert record["description"] == "Custom"
    assert record["_params"] == {"version_prefix": "/v2"}


def test_doc_preset_flat_form_falls_back_to_default_for_unset_params(monkeypatch):
    """A declared parameter not supplied by the caller is *not* added
    to ``_params`` — defaults are applied at substitution time, not
    record-construction time."""
    from unitysvc_data import presets as p

    target = "s3_code_example_v1"
    monkeypatch.setitem(p._PRESET_PARAMETERS, target, {"version_prefix": "/v1"})

    record = doc_preset(target, description="X")
    assert record["description"] == "X"
    assert "_params" not in record


def test_doc_preset_flat_form_unknown_key_rejected_via_factory(monkeypatch):
    """A key that's neither a declared param nor in OVERRIDABLE goes
    through the factory, which rejects it with the existing
    ``Cannot override`` message."""
    from unitysvc_data import presets as p

    target = "s3_code_example_v1"
    monkeypatch.setitem(p._PRESET_PARAMETERS, target, {"version_prefix": "/v1"})

    with pytest.raises(ValueError, match="Cannot override"):
        doc_preset(target, totally_unknown_thing="x")


def test_doc_preset_flat_form_param_value_must_be_string(monkeypatch):
    from unitysvc_data import presets as p

    target = "s3_code_example_v1"
    monkeypatch.setitem(p._PRESET_PARAMETERS, target, {"version_prefix": "/v1"})

    with pytest.raises(ValueError, match="must be a string"):
        doc_preset(target, version_prefix=123)


def test_file_preset_flat_form_substitutes(monkeypatch, tmp_path):
    """End-to-end flat-form substitution via file_preset: redirect a
    preset's bundled file to a tmp-path body that uses the placeholder,
    then verify the kwarg propagates."""
    from unitysvc_data import presets as p

    body_path = tmp_path / "param_body.sh"
    body_path.write_text('echo "${__version_prefix__}/chat/completions"\n')

    target = "s3_connectivity_v1"
    monkeypatch.setitem(
        p._PRESET_RECORDS[target], "file_path", str(body_path)
    )
    monkeypatch.setitem(p._PRESET_PARAMETERS, target, {"version_prefix": "/v1"})

    # Default: applies the declared default
    assert file_preset(target) == 'echo "/v1/chat/completions"\n'

    # Override: kwarg wins
    assert (
        file_preset(target, version_prefix="/compatibility/v1")
        == 'echo "/compatibility/v1/chat/completions"\n'
    )


def test_substitute_params_replaces_default_when_no_override():
    """White-box test on the substitution helper.  Uses the public
    behaviour via a synthetic preset entry."""
    from unitysvc_data.presets import _substitute_params

    body = "url = ${__path__}/v1/messages"
    out = _substitute_params(
        body,
        declared={"path": "/default"},
        overrides={},
        preset_name="synthetic",
    )
    assert out == "url = /default/v1/messages"


def test_substitute_params_replaces_with_override_value():
    from unitysvc_data.presets import _substitute_params

    body = "url = ${__path__}/v1/messages"
    out = _substitute_params(
        body,
        declared={"path": "/default"},
        overrides={"path": "/compatibility"},
        preset_name="synthetic",
    )
    assert out == "url = /compatibility/v1/messages"


def test_substitute_params_handles_multiple_references():
    from unitysvc_data.presets import _substitute_params

    body = "${__a__} ${__b__} ${__a__}"
    out = _substitute_params(
        body,
        declared={"a": "X", "b": "Y"},
        overrides={"a": "1", "b": "2"},
        preset_name="synthetic",
    )
    assert out == "1 2 1"


def test_substitute_params_leaves_shell_var_references_alone():
    """Single-underscore / no-underscore ${VAR} references must not
    match — they're shell variables in .sh.j2 files, not preset
    parameters."""
    from unitysvc_data.presets import _substitute_params

    body = 'echo "${TMPDIR:-/tmp}/${__suffix__}/${HOME}"'
    out = _substitute_params(
        body,
        declared={"suffix": "out"},
        overrides={},
        preset_name="synthetic",
    )
    assert out == 'echo "${TMPDIR:-/tmp}/out/${HOME}"'


def test_substitute_params_leaves_undeclared_references_alone():
    """Best-effort substitution: undeclared ``${__name__}`` placeholders
    pass through verbatim rather than raising.  Authors may have
    literal placeholders for documentation, future parameters, etc."""
    from unitysvc_data.presets import _substitute_params

    out = _substitute_params(
        "declared=${__path__} undeclared=${__missing__}",
        declared={"path": "/default"},
        overrides={},
        preset_name="synthetic",
    )
    assert out == "declared=/default undeclared=${__missing__}"


def test_parse_source_accepts_unknown_keys_message_lists_params():
    """Sentinel parsing errors should mention $params is a valid key."""
    with pytest.raises(ValueError, match=r"'\$params'"):
        doc_preset({"$preset": "s3_connectivity_v1", "$nope": {}})
