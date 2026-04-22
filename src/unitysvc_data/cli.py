"""``usvc_data`` — browse and expand bundled presets from the shell.

Subcommands:

- ``usvc_data list`` — print every preset name (versioned + aliases).
- ``usvc_data info <name>`` — print a preset's README prose (metadata
  is shown on the list view / doc-preset output).
- ``usvc_data doc-preset <name> [--with JSON]`` — print the expanded
  document record as JSON on stdout.
- ``usvc_data file-preset <name>`` — print the raw content of the
  preset's bundled file on stdout. For ``.j2`` templates the raw
  template source is returned — Jinja2 rendering is the caller's
  responsibility (the sellers SDK does it per-listing).

Example:

    $ usvc_data doc-preset s3_connectivity --with '{"description": "ours"}'
    {
      "category": "connectivity_test",
      "description": "ours",
      ...
    }
    $ usvc_data file-preset s3_connectivity > /tmp/smoke.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from . import ALIASES, MANIFEST, PRESETS, __version__, doc_preset, file_preset

# Matches a TOML front-matter block delimited by '+++' lines at the top
# of a README. Mirrors the parser in tools/build.py.
_FRONT_MATTER_RE = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.DOTALL)


def _parse_with(value: str | None) -> tuple[dict[str, Any] | None, str | None]:
    """Parse the ``--with`` JSON argument.

    Returns ``(overrides, None)`` on success or ``(None, error_message)``
    on failure. Callers print the error to stderr and return 1 — this
    keeps error handling symmetric with the other subcommands (all
    errors flow through the ``main()`` return value; no ``SystemExit``
    bypass).
    """
    if value is None:
        return {}, None
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        return None, f"--with must be a JSON object: {exc}"
    if not isinstance(parsed, dict):
        return None, f"--with must be a JSON object, got {type(parsed).__name__}"
    return parsed, None


def _cmd_list(args: argparse.Namespace) -> int:
    versioned = sorted(MANIFEST["presets"])
    aliases = sorted(ALIASES)

    if args.json:
        json.dump(
            {"versioned": versioned, "aliases": {a: ALIASES[a] for a in aliases}},
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0

    print(f"Versioned presets ({len(versioned)}):")
    for name in versioned:
        entry = MANIFEST["presets"][name]
        print(f"  {name:40s}  {entry['category']:20s}  {entry['mime_type']}")
    print()
    print(f"Aliases ({len(aliases)}):")
    for alias in aliases:
        print(f"  {alias:40s}  -> {ALIASES[alias]}")
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    """Print the README prose (front-matter stripped) for a preset."""
    name = args.name
    # Resolve via the same alias logic the runtime uses.
    target = ALIASES.get(name, name)
    entry = MANIFEST["presets"].get(target)
    if entry is None:
        print(
            f"error: Unknown preset: {name!r}. Available: {sorted(set(MANIFEST['presets']) | set(ALIASES))!r}",
            file=sys.stderr,
        )
        return 1

    # source_readme is stored relative to examples/; resolve through
    # the package's example_path so it works from any install layout.
    from . import example_path

    text = example_path(entry["source_readme"]).read_text(encoding="utf-8")
    match = _FRONT_MATTER_RE.match(text)
    prose = text[match.end():] if match else text
    # Strip leading blank lines so the first visible line is the first
    # heading / paragraph of the README.
    sys.stdout.write(prose.lstrip("\n"))
    if not prose.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _cmd_doc_preset(args: argparse.Namespace) -> int:
    overrides, err = _parse_with(args.with_json)
    if err is not None:
        print(f"error: {err}", file=sys.stderr)
        return 1
    try:
        record = doc_preset(args.name, **overrides)
    except (KeyError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    indent = None if args.compact else 2
    json.dump(record, sys.stdout, indent=indent, sort_keys=args.sort_keys)
    sys.stdout.write("\n")
    return 0


def _cmd_file_preset(args: argparse.Namespace) -> int:
    try:
        content = file_preset(args.name)
    except (KeyError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    # Write exactly what the file contains — don't add/trim a trailing
    # newline. Consumers piping to a file should get byte-identical
    # content to the bundled source.
    sys.stdout.write(content)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="usvc_data",
        description="Browse and expand presets bundled with unitysvc-data.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    p_list = sub.add_parser("list", help="List every bundled preset.")
    p_list.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    p_list.set_defaults(func=_cmd_list)

    p_info = sub.add_parser(
        "info",
        help="Print the README prose for a preset.",
        description=(
            "Print the human-readable description of a preset — the "
            "family README with its TOML front-matter stripped off. "
            "Handy for browsing what a preset does without opening the "
            "GitHub tree."
        ),
    )
    p_info.add_argument("name", help="Preset name (versioned or alias).")
    p_info.set_defaults(func=_cmd_info)

    p_doc = sub.add_parser(
        "doc-preset",
        help="Print the expanded document record for a preset as JSON.",
    )
    p_doc.add_argument("name", help="Preset name (versioned or alias).")
    p_doc.add_argument(
        "--with",
        dest="with_json",
        metavar="JSON",
        help=(
            "Per-field overrides as a JSON object. "
            "Allowed keys: description, is_active, is_public, meta."
        ),
    )
    p_doc.add_argument("--compact", action="store_true", help="Emit single-line JSON.")
    p_doc.add_argument(
        "--sort-keys",
        action="store_true",
        help="Sort JSON keys for stable diffs.",
    )
    p_doc.set_defaults(func=_cmd_doc_preset)

    p_file = sub.add_parser(
        "file-preset",
        help="Print the raw content of a preset's bundled example file.",
        description=(
            "Print the raw content of a preset's bundled example file. "
            "For .j2 templates the output is the raw template source — "
            "Jinja2 constructs like '{% if ... %}' are preserved verbatim "
            "and are expected to be rendered later by the SDK with "
            "per-listing context. Piping the result to an executable "
            "file only works cleanly for non-.j2 presets."
        ),
    )
    p_file.add_argument("name", help="Preset name (versioned or alias).")
    p_file.set_defaults(func=_cmd_file_preset)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


# Silence unused-import warnings where PRESETS is only kept for debugging
# at the REPL via ``python -m unitysvc_data.cli``.
_ = PRESETS


if __name__ == "__main__":
    raise SystemExit(main())
