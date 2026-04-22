"""Tests for the ``usvc_data`` CLI."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from unitysvc_data import doc_preset, file_preset
from unitysvc_data.cli import main


def _run(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        rc = main(list(argv))
    return rc, out.getvalue(), err.getvalue()


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_cli_list_human():
    rc, out, _ = _run("list")
    assert rc == 0
    assert "Versioned presets" in out
    assert "s3_connectivity_v1" in out
    assert "s3_connectivity  " in out  # alias line
    assert "-> s3_connectivity_v1" in out


def test_cli_list_json():
    rc, out, _ = _run("list", "--json")
    assert rc == 0
    parsed = json.loads(out)
    assert "s3_connectivity_v1" in parsed["versioned"]
    assert parsed["aliases"]["s3_connectivity"] == "s3_connectivity_v1"


# ---------------------------------------------------------------------------
# doc-preset
# ---------------------------------------------------------------------------


def test_cli_doc_preset_default_is_pretty_json():
    rc, out, _ = _run("doc-preset", "s3_connectivity_v1")
    assert rc == 0
    # indent=2 means newlines are present.
    assert "\n" in out.strip()
    parsed = json.loads(out)
    assert parsed == doc_preset("s3_connectivity_v1")


def test_cli_doc_preset_alias_matches_versioned():
    _, alias_out, _ = _run("doc-preset", "s3_connectivity")
    _, v1_out, _ = _run("doc-preset", "s3_connectivity_v1")
    assert json.loads(alias_out) == json.loads(v1_out)


def test_cli_doc_preset_with_overrides():
    rc, out, _ = _run(
        "doc-preset",
        "s3_code_example",
        "--with",
        '{"description": "Customised", "is_public": false}',
    )
    assert rc == 0
    parsed = json.loads(out)
    assert parsed["description"] == "Customised"
    assert parsed["is_public"] is False


def test_cli_doc_preset_compact_emits_single_line():
    rc, out, _ = _run("doc-preset", "s3_connectivity_v1", "--compact")
    assert rc == 0
    # Single-line JSON followed by a trailing newline.
    assert out.count("\n") == 1
    assert json.loads(out)


def test_cli_doc_preset_sort_keys():
    rc, out, _ = _run("doc-preset", "s3_connectivity_v1", "--sort-keys")
    assert rc == 0
    # Top-level keys are emitted at two-space indent; anything deeper
    # is nested. Extract only lines starting with exactly two spaces.
    top_keys = [
        line.split('"')[1]
        for line in out.splitlines()
        if line.startswith('  "') and not line.startswith("   ")
    ]
    assert top_keys == sorted(top_keys)


# --- doc-preset error paths ------------------------------------------------


def test_cli_doc_preset_unknown_name():
    rc, out, err = _run("doc-preset", "no_such_preset")
    assert rc == 1
    assert not out
    assert "Unknown preset" in err


def test_cli_doc_preset_forbidden_override():
    rc, _, err = _run(
        "doc-preset", "s3_connectivity_v1", "--with", '{"category": "other"}'
    )
    assert rc == 1
    assert "Cannot override" in err


def test_cli_doc_preset_invalid_with_json():
    rc, out, err = _run("doc-preset", "s3_connectivity_v1", "--with", "not json")
    assert rc == 1
    assert not out
    assert "must be a JSON object" in err


def test_cli_doc_preset_with_non_object_json():
    rc, out, err = _run("doc-preset", "s3_connectivity_v1", "--with", "[1, 2, 3]")
    assert rc == 1
    assert not out
    assert "must be a JSON object" in err


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


def test_cli_info_prints_readme_prose():
    rc, out, _ = _run("info", "s3_connectivity_v1")
    assert rc == 0
    # Should NOT include TOML front-matter.
    assert "+++" not in out
    assert "preset_name =" not in out
    # Should include the expected prose heading.
    assert "s3 / connectivity" in out


def test_cli_info_alias_resolves_to_same_readme():
    _, alias_out, _ = _run("info", "s3_connectivity")
    _, v1_out, _ = _run("info", "s3_connectivity_v1")
    assert alias_out == v1_out


def test_cli_info_unknown_name():
    rc, out, err = _run("info", "no_such_preset")
    assert rc == 1
    assert not out
    assert "Unknown preset" in err


# ---------------------------------------------------------------------------
# file-preset
# ---------------------------------------------------------------------------


def test_cli_file_preset_outputs_raw_content():
    rc, out, _ = _run("file-preset", "s3_connectivity_v1")
    assert rc == 0
    assert out == file_preset("s3_connectivity_v1")


def test_cli_file_preset_alias_matches_versioned():
    _, alias_out, _ = _run("file-preset", "s3_connectivity")
    _, v1_out, _ = _run("file-preset", "s3_connectivity_v1")
    assert alias_out == v1_out


def test_cli_file_preset_unknown_name():
    rc, out, err = _run("file-preset", "no_such_preset")
    assert rc == 1
    assert not out
    assert "Unknown preset" in err


# ---------------------------------------------------------------------------
# argparse-level errors
# ---------------------------------------------------------------------------


def test_cli_requires_subcommand():
    with pytest.raises(SystemExit):
        _run()


def test_cli_version(capsys):
    # argparse writes --version to stdout and raises SystemExit(0)
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    from unitysvc_data import __version__

    assert __version__ in captured.out
