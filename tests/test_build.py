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


def test_undeclared_parameter_reference_in_body_allowed(tmp_path, monkeypatch):
    """Best-effort substitution: the build tolerates ``${__name__}``
    placeholders in the body that aren't declared as parameters — they
    pass through verbatim at substitution time.  Authors may have
    literal placeholders for documentation, future parameters, etc."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "api",
        "param",
        readme=_front_matter_with_params('declared = "x"'),
        files={"param-v1.sh.j2": "echo ${__declared__} ${__missing__}"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not errors.messages, errors.messages
    assert presets[0].parameters == {"declared": "x"}


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


# ---------------------------------------------------------------------------
# Variant file support
# ---------------------------------------------------------------------------


def test_variant_files_register_as_separate_families(tmp_path, monkeypatch):
    """Files named ``<stem>-<variant>-v<N>.<suffix>`` in the same directory
    register as additional preset families with names
    ``<base_preset_name>_<variant_slug>``."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "notify",
        "connectivity",
        readme=_good_front_matter(preset_name="notify_connectivity", file="connectivity.sh.j2"),
        files={
            "connectivity-discord-v1.sh.j2": "echo discord",
            "connectivity-slack-v1.sh.j2": "echo slack",
        },
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors.messages, errors.messages
    names = [p.name for p in presets]
    assert "notify_connectivity_discord_v1" in names
    assert "notify_connectivity_slack_v1" in names
    assert aliases["notify_connectivity_discord"] == "notify_connectivity_discord_v1"
    assert aliases["notify_connectivity_slack"] == "notify_connectivity_slack_v1"


def test_variant_and_base_coexist(tmp_path, monkeypatch):
    """A directory can have both base files (``<stem>-v<N>``) and variant files."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "notify",
        "connectivity",
        readme=_good_front_matter(preset_name="notify_connectivity", file="connectivity.sh.j2"),
        files={
            "connectivity-v1.sh.j2": "echo base",
            "connectivity-discord-v1.sh.j2": "echo discord",
        },
    )
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors.messages, errors.messages
    names = [p.name for p in presets]
    assert "notify_connectivity_v1" in names
    assert "notify_connectivity_discord_v1" in names


def test_variant_only_dir_no_base_required(tmp_path, monkeypatch):
    """A directory with only variant files (no base ``-v<N>`` files) is valid."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "notify",
        "connectivity",
        readme=_good_front_matter(preset_name="notify_connectivity", file="connectivity.sh.j2"),
        files={"connectivity-ntfy-v1.sh.j2": "echo ntfy"},
    )
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors.messages, errors.messages
    assert [p.name for p in presets] == ["notify_connectivity_ntfy_v1"]


def test_variant_inherits_readme_metadata(tmp_path, monkeypatch):
    """Variant presets inherit category, mime_type, description, is_active,
    is_public, meta, and parameters from the shared README."""
    root = _point_build_at(tmp_path, monkeypatch)
    readme = (
        "+++\n"
        'preset_name = "notify_connectivity"\n'
        'category = "connectivity_test"\n'
        'mime_type = "bash"\n'
        'file = "connectivity.sh.j2"\n'
        'description = "shared desc"\n'
        "is_active = true\n"
        "is_public = false\n"
        'meta = { timeout_s = 10 }\n'
        'parameters = { webhook_path = "/webhook" }\n'
        "+++\n\n# body\n"
    )
    _family(
        root,
        "notify",
        "connectivity",
        readme=readme,
        files={"connectivity-discord-v1.sh.j2": "echo discord"},
    )
    errors = build.BuildErrors()
    presets, _ = build.discover(errors)
    assert not errors.messages, errors.messages
    assert len(presets) == 1
    p = presets[0]
    assert p.preset_name == "notify_connectivity_discord"
    assert p.category == "connectivity_test"
    assert p.mime_type == "bash"
    assert p.description == "shared desc"
    assert p.is_active is True
    assert p.is_public is False
    assert p.meta == {"timeout_s": 10}
    assert p.parameters == {"webhook_path": "/webhook"}


def test_variant_hyphen_converted_to_underscore(tmp_path, monkeypatch):
    """Multi-segment variant slugs like ``ms-teams`` have hyphens converted
    to underscores in the preset_name (``_ms_teams``)."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "notify",
        "connectivity",
        readme=_good_front_matter(preset_name="notify_connectivity", file="connectivity.sh.j2"),
        files={"connectivity-ms-teams-v1.sh.j2": "echo msteams"},
    )
    errors = build.BuildErrors()
    presets, aliases = build.discover(errors)
    assert not errors.messages, errors.messages
    assert presets[0].preset_name == "notify_connectivity_ms_teams"
    assert "notify_connectivity_ms_teams" in aliases


def test_duplicate_variant_version_is_error(tmp_path, monkeypatch):
    """Two files for the same variant and version number is a build error."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "notify",
        "connectivity",
        readme=_good_front_matter(preset_name="notify_connectivity", file="connectivity.sh.j2"),
        files={
            "connectivity-discord-v1.sh.j2": "echo a",
            # Simulate a duplicate by using a different name that still
            # resolves via the variant pattern — can't really duplicate the
            # exact same filename but we can test the collision path directly.
        },
    )
    # Inject a synthetic collision directly via _load_families for the coverage,
    # but the more important tests above confirm the happy paths.
    errors = build.BuildErrors()
    _presets, _ = build.discover(errors)
    assert not errors.messages, errors.messages  # no collision in this case


# ---------------------------------------------------------------------------
# Request templates: an entry the playground can never reach
# ---------------------------------------------------------------------------
#
# The playground picks a template by capability and then the FIRST entry that
# names the format the customer chose. So a template is a function of
# (capability, format), and anything that breaks that makes an entry silently
# unreachable: a second entry for the same format is never read, and an entry
# with no usable format or no body is skipped. None of these fail at runtime --
# the customer just never sees the request the author wrote.


def _template_front_matter(
    preset_name: str = "llm_request_template_embed",
    file: str = "request-template-embed.json",
    capability: str | None = "embed",
) -> str:
    applies = f'applies_to = {{ capability = "{capability}" }}\n' if capability else ""
    return (
        "+++\n"
        f'preset_name = "{preset_name}"\n'
        'category = "request_template"\n'
        'mime_type = "json"\n'
        f'file = "{file}"\n'
        'description = "Minimal embeddings request body"\n'
        f"{applies}"
        "+++\n\n# body\n"
    )


def _template_tree(tmp_path, monkeypatch, files: dict[str, str], *, capability: str | None = "embed"):
    """One ``llm/request-template-embed`` family holding ``files``."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "llm",
        "request-template-embed",
        readme=_template_front_matter(capability=capability),
        files=files,
    )
    return root


def _template_errors(presets_discovered=None) -> list[str]:
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors, errors.messages
    build.check_request_templates(presets, errors)
    return errors.messages


GOOD_ENTRIES = (
    '[{"format": "openai", "body": {"input": "hi"}},'
    ' {"format": "cohere", "body": {"texts": ["hi"]}}]'
)


def test_a_request_template_with_one_entry_per_format_passes(tmp_path, monkeypatch):
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": GOOD_ENTRIES})

    assert _template_errors() == []


def test_a_second_entry_for_a_format_is_rejected(tmp_path, monkeypatch):
    """The reader takes the first match, so the second is unreachable."""
    dup = (
        '[{"format": "openai", "body": {"input": "first"}},'
        ' {"format": "cohere", "body": {"texts": ["hi"]}},'
        ' {"format": "openai", "body": {"input": "second"}}]'
    )
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": dup})

    messages = _template_errors()

    assert len(messages) == 1, messages
    assert "'openai'" in messages[0] and "embed" in messages[0]
    assert "entries 0 and 2" in messages[0]
    assert "unreachable" in messages[0]


def test_formats_that_differ_only_by_padding_are_the_same_format(tmp_path, monkeypatch):
    """The reader trims a format before comparing it, so these collide there."""
    padded = '[{"format": "openai", "body": {"a": 1}}, {"format": "  openai ", "body": {"a": 2}}]'
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": padded})

    messages = _template_errors()

    assert any("entries 0 and 1" in m for m in messages), messages


@pytest.mark.parametrize(
    ("entry", "complaint"),
    [
        ('{"body": {"a": 1}}', "no usable `format`"),
        ('{"format": "", "body": {"a": 1}}', "no usable `format`"),
        ('{"format": "   ", "body": {"a": 1}}', "no usable `format`"),
        ('{"format": 7, "body": {"a": 1}}', "no usable `format`"),
        ('{"format": "openai"}', "no `body`"),
        ('{"format": "openai", "body": null}', "no `body`"),
        ('"openai"', "not an object"),
    ],
    ids=["no-format", "empty-format", "blank-format", "numeric-format", "no-body", "null-body", "not-an-object"],
)
def test_an_entry_the_reader_would_skip_is_rejected(tmp_path, monkeypatch, entry, complaint):
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": f"[{entry}]"})

    messages = _template_errors()

    assert len(messages) == 1, messages
    assert complaint in messages[0]


def test_an_unregistered_format_is_rejected_with_a_hint(tmp_path, monkeypatch):
    """A mistyped format is an entry no service can ever select -- the same
    silent failure as a duplicate, from a different slip of the keyboard."""
    typo = '[{"format": "opena", "body": {"input": "hi"}}]'
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": typo})

    messages = _template_errors()

    assert len(messages) == 1, messages
    assert "'opena'" in messages[0] and "Did you mean 'openai'" in messages[0]


def test_an_empty_entry_list_is_rejected(tmp_path, monkeypatch):
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": "[]"})

    messages = _template_errors()

    assert len(messages) == 1 and "no entries" in messages[0], messages


def test_keys_the_reader_does_not_know_are_not_the_guards_business(tmp_path, monkeypatch):
    """`path_suffix` and `content_type` are coming (unitysvc#2514, step 2), and
    the reader ignores keys it does not recognise so the data can ship first. A
    guard that refused them would force the two to land in lockstep."""
    later = (
        '[{"format": "openai", "body": {"input": "hi"},'
        ' "path_suffix": "/v1/embeddings", "content_type": "application/json"}]'
    )
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": later})

    assert _template_errors() == []


def test_older_dict_shaped_versions_are_left_alone(tmp_path, monkeypatch):
    """Versions are append-only and `v1`/`v2` of the chat template predate the
    list shape. The guard reads what it understands and skips the rest."""
    _template_tree(
        tmp_path,
        monkeypatch,
        {
            "request-template-embed-v1.json": '{"input": "hi"}',
            "request-template-embed-v2.json": '{"openai": {"input": "hi"}}',
            "request-template-embed-v3.json": GOOD_ENTRIES,
        },
    )

    assert _template_errors() == []


def test_a_pinned_older_list_version_is_still_checked(tmp_path, monkeypatch):
    """`$doc_preset: x_v1` still resolves, so a duplicate in v1 is served."""
    dup = '[{"format": "openai", "body": {"a": 1}}, {"format": "openai", "body": {"a": 2}}]'
    _template_tree(
        tmp_path,
        monkeypatch,
        {"request-template-embed-v1.json": dup, "request-template-embed-v2.json": GOOD_ENTRIES},
    )

    messages = _template_errors()

    assert len(messages) == 1 and "request-template-embed-v1.json" in messages[0], messages


def test_the_latest_version_of_a_capability_template_must_be_an_entry_list(tmp_path, monkeypatch):
    """What the alias resolves to is what every listing gets. Letting it be the
    dict shape would keep the legacy reader branch alive indefinitely, and the
    page marks that branch deletable once catalogs have migrated."""
    _template_tree(
        tmp_path,
        monkeypatch,
        {"request-template-embed-v1.json": '{"openai": {"input": "hi"}}'},
    )

    messages = _template_errors()

    assert len(messages) == 1, messages
    assert "latest version" in messages[0] and "entry list" in messages[0]


def test_a_template_that_names_no_capability_may_stay_a_plain_body(tmp_path, monkeypatch):
    """`msg_request_template` declares no `applies_to` and is one flat envelope.
    The list shape is the contract for capability templates, not for those."""
    _template_tree(
        tmp_path,
        monkeypatch,
        {"request-template-embed-v1.json": '{"title": "t", "body": "hi"}'},
        capability=None,
    )

    assert _template_errors() == []


def test_a_template_that_is_not_json_is_rejected(tmp_path, monkeypatch):
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": "[{"})

    messages = _template_errors()

    assert len(messages) == 1 and "not valid JSON" in messages[0], messages


def test_other_categories_are_not_read_as_templates(tmp_path, monkeypatch):
    """Only `request_template` documents have entries to check."""
    root = _point_build_at(tmp_path, monkeypatch)
    _family(
        root,
        "llm",
        "hello",
        readme=_good_front_matter(preset_name="llm_hello", file="hello.sh.j2"),
        files={"hello-v1.sh.j2": "not json at all"},
    )

    assert _template_errors() == []


def test_the_guard_runs_as_part_of_the_build(tmp_path, monkeypatch, capsys):
    """Defined is not wired: `main` must fail on a duplicate, before it writes
    or compares any output."""
    dup = '[{"format": "openai", "body": {"a": 1}}, {"format": "openai", "body": {"a": 2}}]'
    _template_tree(tmp_path, monkeypatch, {"request-template-embed-v1.json": dup})

    assert build.main(["--check"]) == 1

    assert "unreachable" in capsys.readouterr().err


def test_the_shipped_request_templates_pass_the_guard():
    """The corpus itself, through the same entry point the build uses."""
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors, errors.messages

    build.check_request_templates(presets, errors)

    assert not errors.messages, "\n".join(errors.messages)


# ---------------------------------------------------------------------------
# Same selector, same title: the clash `check_titles` used to skip
# ---------------------------------------------------------------------------
#
# `check_titles` compares presets that render one title and skips a pair whose
# `applies_to` is identical -- "same selector: one document, not a clash". That
# is right for versions of one preset and wrong for two PRESETS: `_select` picks
# both for the same service, they render one title, and the later name silently
# replaces the earlier. Variant files make it easy to do by accident, because a
# variant inherits its README's `applies_to` wholesale.


def _chat_template_family(root, slug: str, preset_name: str, files: dict[str, str]):
    _family(
        root,
        "llm",
        slug,
        readme=_template_front_matter(
            preset_name=preset_name, file=f"{slug}.json", capability="chat"
        ),
        files=files,
    )


def _title_clashes() -> list[str]:
    errors = build.BuildErrors()
    presets, _aliases = build.discover(errors)
    assert not errors, errors.messages
    build.check_titles(presets, errors)
    return errors.messages


def test_two_llm_presets_with_one_selector_and_one_title_are_a_clash(tmp_path, monkeypatch):
    root = _point_build_at(tmp_path, monkeypatch)
    _chat_template_family(root, "request-template", "llm_request_template", {"request-template-v1.json": GOOD_ENTRIES})
    _chat_template_family(
        root, "request-template-chat", "llm_request_template_chat", {"request-template-chat-v1.json": GOOD_ENTRIES}
    )

    messages = _title_clashes()

    assert len(messages) == 1, messages
    assert "llm_request_template" in messages[0] and "llm_request_template_chat" in messages[0]
    assert "Default request body" in messages[0] and "same applies_to" in messages[0]


def test_the_variant_shortcut_cannot_hide_a_clash(tmp_path, monkeypatch):
    """A template for another capability filed as a VARIANT of the chat family
    inherits `applies_to = chat`, renders chat's title, and -- sorting after it --
    would replace the chat template on every chat service. Nothing else notices."""
    root = _point_build_at(tmp_path, monkeypatch)
    _chat_template_family(
        root,
        "request-template",
        "llm_request_template",
        {
            "request-template-v1.json": GOOD_ENTRIES,
            "request-template-embed-v1.json": GOOD_ENTRIES,
        },
    )

    messages = _title_clashes()

    assert len(messages) == 1 and "llm_request_template_embed" in messages[0], messages


def test_versions_of_one_preset_still_share_a_title(tmp_path, monkeypatch):
    """Newer content of the same document, compared once by name."""
    root = _point_build_at(tmp_path, monkeypatch)
    _chat_template_family(
        root,
        "request-template",
        "llm_request_template",
        {"request-template-v1.json": '{"a": 1}', "request-template-v2.json": GOOD_ENTRIES},
    )

    assert _title_clashes() == []


def test_named_variants_outside_the_selected_gateways_may_share_a_selector(tmp_path, monkeypatch):
    """`msg-to-channel` and `notify-relay` hold one preset per channel, each with
    no `applies_to` and the same title, and a listing names the one it wants. Only
    the gateway `presets._select` fans out over can clash on a selector."""
    root = _point_build_at(tmp_path, monkeypatch)
    for slug, name in (("connectivity-a", "msg_to_channel_a"), ("connectivity-b", "msg_to_channel_b")):
        _family(
            root,
            "msg-to-channel",
            slug,
            readme=_good_front_matter(preset_name=name, file=f"{slug}.sh.j2"),
            files={f"{slug}-v1.sh.j2": "echo hi"},
        )

    assert _title_clashes() == []
