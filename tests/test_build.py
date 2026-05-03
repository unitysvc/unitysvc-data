"""Unit tests for ``tools/build.py`` validation branches.

The runtime tests in ``test_presets.py`` cover the happy-path manifest
once it's been generated. These tests exercise the validator itself
against synthetic example trees so we catch regressions in the
branches that sellers will actually hit when they author a preset
incorrectly.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_build_module():
    """Import ``tools/build.py`` as a module without adding tools/ to sys.path."""
    path = REPO_ROOT / "tools" / "build.py"
    spec = importlib.util.spec_from_file_location("unitysvc_data_build_under_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


build = _load_build_module()


# ---------------------------------------------------------------------------
# Fixture helper: build a synthetic examples tree rooted at tmp_path
# ---------------------------------------------------------------------------


def _point_build_at(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect the build module to read from ``tmp_path/examples``."""
    examples_root = tmp_path / "examples"
    examples_root.mkdir()
    monkeypatch.setattr(build, "EXAMPLES_DIR", examples_root)
    monkeypatch.setattr(build, "ROOT", tmp_path)
    return examples_root


def _family(
    examples_root: Path,
    gateway: str,
    slug: str,
    *,
    readme: str,
    files: dict[str, str],
) -> Path:
    """Create one family dir with the given README and files."""
    family_dir = examples_root / gateway / slug
    family_dir.mkdir(parents=True)
    (family_dir / "README.md").write_text(readme, encoding="utf-8")
    for name, content in files.items():
        (family_dir / name).write_text(content, encoding="utf-8")
    return family_dir


def _good_front_matter(preset_name: str = "api_hello", file: str = "hello.sh.j2") -> str:
    return (
        "+++\n"
        f'preset_name = "{preset_name}"\n'
        'category = "connectivity_test"\n'
        'mime_type = "bash"\n'
        f'file = "{file}"\n'
        'description = "Hello"\n'
        "+++\n\n# body\n"
    )


# ---------------------------------------------------------------------------
# Happy path sanity
# ---------------------------------------------------------------------------


def test_discover_happy_path(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(),
        files={"hello-v1.sh.j2": "echo hi"},
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors, errors.messages
    assert [p.name for p in presets] == ["api_hello_v1"]
    assert aliases == {"api_hello": "api_hello_v1"}


def test_multiple_versions_auto_discovered_and_alias_points_at_highest(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(),
        files={
            "hello-v1.sh.j2": "echo v1",
            "hello-v2.sh.j2": "echo v2",
            "hello-v3.sh.j2": "echo v3",
        },
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors
    assert [p.version for p in presets] == [1, 2, 3]
    assert aliases == {"api_hello": "api_hello_v3"}


# ---------------------------------------------------------------------------
# Validation error paths
# ---------------------------------------------------------------------------


def test_duplicate_preset_name_across_families(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(preset_name="shared_name"),
        files={"hello-v1.sh.j2": "x"},
    )
    _family(
        root,
        "s3",
        "world",
        readme=_good_front_matter(preset_name="shared_name", file="world.sh.j2"),
        files={"world-v1.sh.j2": "x"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    # One family survives; the second fails the uniqueness check.
    assert len(presets) == 1
    assert any("duplicate preset_name 'shared_name'" in m for m in errors.messages)


def test_preset_name_with_version_suffix_rejected(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(preset_name="api_hello_v1"),
        files={"hello-v1.sh.j2": "x"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not presets
    assert any("must not end with '_v<N>'" in m for m in errors.messages)


def test_preset_name_must_be_identifier(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(preset_name="1-bad-name"),
        files={"hello-v1.sh.j2": "x"},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("Python-style identifier" in m for m in errors.messages)


def test_missing_required_field(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    readme = (
        "+++\n"
        'preset_name = "api_hello"\n'
        'mime_type = "bash"\n'       # 'category' intentionally missing
        'file = "hello.sh.j2"\n'
        'description = "d"\n'
        "+++\n\n# body\n"
    )
    _family(root, "api", "hello", readme=readme, files={"hello-v1.sh.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("missing required front-matter field(s)" in m for m in errors.messages)


def test_unknown_front_matter_field_rejected(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    readme = _good_front_matter() + "\n"  # trailing content fine
    readme = readme.replace(
        'description = "Hello"\n',
        'description = "Hello"\nrandom_field = true\n',
    )
    _family(root, "api", "hello", readme=readme, files={"hello-v1.sh.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("unknown front-matter field(s)" in m for m in errors.messages)


def test_mime_extension_mismatch(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    # mime_type claims bash but file has .py extension.
    readme = _good_front_matter(file="hello.py.j2").replace(
        'mime_type = "bash"', 'mime_type = "bash"'
    )
    _family(root, "api", "hello", readme=readme, files={"hello-v1.py.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("does not match mime_type" in m for m in errors.messages)


def test_unknown_mime_type(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    readme = _good_front_matter().replace(
        'mime_type = "bash"', 'mime_type = "klingon"'
    )
    _family(root, "api", "hello", readme=readme, files={"hello-v1.sh.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("unknown mime_type 'klingon'" in m for m in errors.messages)


def test_file_field_missing_extension(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    readme = _good_front_matter(file="hello")  # no extension
    _family(root, "api", "hello", readme=readme, files={"hello-v1.sh.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("must include an extension" in m for m in errors.messages)


def test_no_versioned_files(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(),
        files={"hello.sh.j2": "x"},  # unversioned
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not presets
    assert any("no files matching" in m for m in errors.messages) or any(
        "do not match version pattern" in m for m in errors.messages
    )


def test_orphan_file_in_family_dir(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(),
        files={
            "hello-v1.sh.j2": "x",
            "stray.txt": "not a version",
        },
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("do not match version pattern" in m for m in errors.messages)


def test_missing_readme(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    family_dir = root / "api" / "hello"
    family_dir.mkdir(parents=True)
    (family_dir / "hello-v1.sh.j2").write_text("x", encoding="utf-8")
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("missing README.md" in m for m in errors.messages)


def test_missing_front_matter(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme="# just prose, no front-matter\n",
        files={"hello-v1.sh.j2": "x"},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("missing TOML front-matter" in m for m in errors.messages)


def test_malformed_toml_front_matter(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    readme = "+++\nthis is not = valid toml [[[\n+++\n\nbody\n"
    _family(root, "api", "hello", readme=readme, files={"hello-v1.sh.j2": "x"})
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("TOML parse error" in m for m in errors.messages)


def test_deterministic_ordering_in_manifest_json(tmp_path, monkeypatch):
    """Manifest rendering should be stable across runs for diff friendliness."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "zzz",
        "later",
        readme=_good_front_matter(preset_name="zzz_later", file="later.sh.j2"),
        files={"later-v1.sh.j2": "x"},
    )
    _family(
        root,
        "aaa",
        "earlier",
        readme=_good_front_matter(preset_name="aaa_earlier", file="earlier.sh.j2"),
        files={"earlier-v1.sh.j2": "x"},
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors

    first = build.render_manifest_json(presets, aliases)
    second = build.render_manifest_json(presets, aliases)
    assert first == second
    # The output must be sorted by preset name.
    assert first.find('"aaa_earlier_v1"') < first.find('"zzz_later_v1"')


# ---------------------------------------------------------------------------
# Preset parameters — front-matter validation + body reference checks
# ---------------------------------------------------------------------------


def _front_matter_with_params(parameters_toml: str, preset_name: str = "api_param") -> str:
    """Front-matter with a custom ``parameters = { ... }`` block."""
    return (
        "+++\n"
        f'preset_name = "{preset_name}"\n'
        'category = "connectivity_test"\n'
        'mime_type = "bash"\n'
        'file = "param.sh.j2"\n'
        'description = "param test"\n'
        f"parameters = {{ {parameters_toml} }}\n"
        "+++\n\n# body\n"
    )


def test_no_parameters_field_defaults_to_empty(tmp_path, monkeypatch):
    """Existing presets without ``parameters`` in front-matter still
    parse, with an empty parameters dict in the manifest entry."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "hello",
        readme=_good_front_matter(),
        files={"hello-v1.sh.j2": "no params here"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not errors.messages
    assert len(presets) == 1
    assert presets[0].parameters == {}


def test_parameters_string_default_accepted(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('path_prefix = ""'),
        files={"param-v1.sh.j2": 'echo "${__path_prefix__}/v1"'},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not errors.messages, errors.messages
    assert presets[0].parameters == {"path_prefix": ""}


def test_parameters_non_string_default_rejected(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params("max_tokens = 100"),
        files={"param-v1.sh.j2": "echo hi"},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("must be a string" in m for m in errors.messages), errors.messages


def test_parameters_bad_name_rejected(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('"bad-name" = ""'),
        files={"param-v1.sh.j2": "echo hi"},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("Python-style identifier" in m for m in errors.messages), errors.messages


def test_parameters_collision_with_metadata_field_rejected(tmp_path, monkeypatch):
    """Parameter names cannot match the metadata override keys
    (description / is_public / is_active / meta) — otherwise the
    flat-form auto-discrimination in doc_preset would be ambiguous."""
    root = _point_build_at(tmp_path, monkeypatch)
    for forbidden in ("description", "is_public", "is_active", "meta"):
        family_dir = root / "api" / f"param-{forbidden}"
        family_dir.mkdir(parents=True)
        (family_dir / "README.md").write_text(
            _front_matter_with_params(
                f'{forbidden} = "x"', preset_name=f"api_param_{forbidden}"
            ),
            encoding="utf-8",
        )
        (family_dir / "param-v1.sh.j2").write_text("echo hi", encoding="utf-8")
    errors = build.BuildErrors()
    build.discover(errors)
    for forbidden in ("description", "is_public", "is_active", "meta"):
        assert any(
            f"parameter name '{forbidden}'" in m and "collides" in m
            for m in errors.messages
        ), f"missing collision error for {forbidden!r}: {errors.messages}"


def test_undeclared_parameter_reference_in_body_rejected(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('declared = "x"'),
        files={"param-v1.sh.j2": "echo ${__declared__} ${__missing__}"},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert any("undeclared parameter" in m and "missing" in m for m in errors.messages), (
        errors.messages
    )


def test_shell_var_references_not_caught_as_parameters(tmp_path, monkeypatch):
    """Single-underscore / no-underscore ``${VAR}`` references are
    shell variables in ``.sh.j2`` files, not preset parameters — the
    build validator must not flag them."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_good_front_matter(),  # declares no parameters
        files={"hello-v1.sh.j2": 'echo "${TMPDIR:-/tmp}/${HOME}/${SHELL}"'},
    )
    errors = build.BuildErrors()
    build.discover(errors)
    assert not any("undeclared parameter" in m for m in errors.messages), errors.messages


def test_declared_but_unused_parameters_allowed(tmp_path, monkeypatch):
    """Declaring a parameter without referencing it isn't a build
    error — sellers may stage params they intend to use in a future
    version of the body."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('unused = "default_value"'),
        files={"param-v1.sh.j2": "no references"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not errors.messages, errors.messages
    assert presets[0].parameters == {"unused": "default_value"}


def test_manifest_json_includes_parameters(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('path_prefix = "/x"'),
        files={"param-v1.sh.j2": 'echo "${__path_prefix__}"'},
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors.messages
    rendered = build.render_manifest_json(presets, aliases)
    import json

    parsed = json.loads(rendered)
    assert parsed["presets"]["api_param_v1"]["parameters"] == {"path_prefix": "/x"}
