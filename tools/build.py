#!/usr/bin/env python3
"""Build the preset manifest and human-readable roster from examples/.

Layout the script expects
-------------------------

Each preset family lives in
``src/unitysvc_data/examples/<gateway>/<family>/`` and contains:

- ``README.md`` with TOML front-matter delimited by ``+++`` lines. The
  front-matter supplies every piece of metadata for the family;
  per-version prose goes underneath the front-matter.
- One file per version, named ``<stem>-v<N>.<suffix>`` where the stem
  and suffix come from the ``file`` front-matter field
  (``file = "connectivity.sh.j2"`` → ``connectivity-v1.sh.j2``,
  ``connectivity-v2.sh.j2``, ...).

Front-matter fields
-------------------

Required:

- ``preset_name`` — the root name the preset is registered as
  (e.g. ``api_connectivity``). Globally unique across the whole tree.
  Each discovered version is exposed as ``<preset_name>_v<N>``, and
  the highest version is also exposed under the bare ``<preset_name>``.
- ``category``, ``mime_type``, ``description`` — standard seller
  document fields.
- ``file`` — the base filename (no version suffix). Used both as the
  pattern for version discovery and as a sanity-check against the
  declared ``mime_type``.

Optional (defaults shown):

- ``is_active`` (``true``), ``is_public`` (``false``), ``meta`` (``{}``).

Multi-document-per-folder (e.g. bundling a resource file with an
example) is out of scope today; when we need it, we'll add an array of
tables to the front-matter. For now, each family has exactly one
``file`` pattern.

Outputs
-------

- ``src/unitysvc_data/_manifest.json`` — machine-readable,
  loaded by :mod:`unitysvc_data.presets` at import time.
- ``MANIFEST.md`` at the repo root — human-readable preset roster.

Run after editing any example. CI runs ``python tools/build.py --check``
and fails if either output is stale.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "src" / "unitysvc_data" / "examples"
MANIFEST_JSON = ROOT / "src" / "unitysvc_data" / "_manifest.json"
MANIFEST_MD = ROOT / "MANIFEST.md"
MANIFEST_VERSION = "1"

REQUIRED_FIELDS: tuple[str, ...] = ("preset_name", "category", "mime_type", "file", "description")
OPTIONAL_FIELDS: dict[str, Any] = {
    "is_active": True,
    "is_public": False,
    "meta": {},
    # ``parameters`` is a TOML table mapping parameter name → string
    # default, e.g. ``parameters = { path_prefix = "" }``.  Each
    # parameter is referenced in the example file as ``${__name__}`` and
    # substituted at preset-fetch time (defaults if no override).  The
    # double-underscore syntax avoids collision with shell-style
    # ``${VAR}`` references in ``.sh.j2`` example files.
    "parameters": {},
}

# Pattern that matches preset parameter references in example bodies.
# Double underscores are required to disambiguate from shell ``${VAR}``
# expansions in ``.sh.j2`` files — sellers writing literal shell vars
# don't accidentally collide with the preset namespace.
PARAM_REFERENCE_RE = re.compile(r"\$\{__([A-Za-z_][A-Za-z0-9_]*)__\}")

# Pattern declared parameter names must match (Python-identifier-like).
PARAM_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

FRONT_MATTER_RE = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n", re.DOTALL)

# mime_type → accepted file extensions (stripped of a trailing ``.j2``).
MIME_EXTENSIONS: dict[str, set[str]] = {
    "bash":       {".sh"},
    "python":     {".py"},
    "json":       {".json"},
    "markdown":   {".md"},
    "typescript": {".ts"},
    "javascript": {".js"},
    "yaml":       {".yaml", ".yml"},
    "text":       {".txt"},
}


@dataclass
class Preset:
    """One concrete (family, version) pair, ready to serialise."""

    name: str                      # e.g. "api_connectivity_v1"
    preset_name: str               # e.g. "api_connectivity" (root / family)
    gateway: str                   # e.g. "api"
    family_slug: str               # e.g. "connectivity" (directory name)
    version: int                   # e.g. 1
    category: str
    mime_type: str
    description: str
    is_active: bool
    is_public: bool
    meta: dict[str, Any]
    parameters: dict[str, str]     # name → default value (always string)
    example_file: str              # relative to examples/
    source_readme: str             # relative to examples/

    def to_manifest_entry(self) -> dict[str, Any]:
        return {
            "preset_name": self.preset_name,
            "version": self.version,
            "category": self.category,
            "mime_type": self.mime_type,
            "description": self.description,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "meta": self.meta,
            "parameters": self.parameters,
            "example_file": self.example_file,
            "source_readme": self.source_readme,
        }


@dataclass
class BuildErrors:
    messages: list[str] = field(default_factory=list)

    def add(self, location: Path, message: str) -> None:
        rel = location.relative_to(ROOT) if location.is_absolute() else location
        self.messages.append(f"{rel}: {message}")

    def __bool__(self) -> bool:
        return bool(self.messages)


# --- Parsing ---------------------------------------------------------------


def parse_front_matter(readme_path: Path, errors: BuildErrors) -> dict[str, Any] | None:
    text = readme_path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        errors.add(readme_path, "missing TOML front-matter (must open and close with '+++')")
        return None
    try:
        return tomllib.loads(match.group(1))
    except tomllib.TOMLDecodeError as exc:
        errors.add(readme_path, f"TOML parse error: {exc}")
        return None


def split_file_field(file_field: str) -> tuple[str, str]:
    """Split ``file`` into (stem, suffix) at the first dot.

    ``connectivity.sh.j2`` -> (``connectivity``, ``sh.j2``).
    ``description.md`` -> (``description``, ``md``).
    """
    stem, sep, suffix = file_field.partition(".")
    if not sep:
        # No extension at all — treat the whole string as the stem with
        # an empty suffix. Callers will typically reject this via
        # mime_type validation.
        return stem, ""
    return stem, suffix


def logical_extension(suffix: str) -> str:
    """Return the content-type extension, ignoring a trailing ``.j2``.

    ``sh.j2`` -> ``.sh``; ``md`` -> ``.md``.
    """
    if suffix.endswith(".j2"):
        suffix = suffix[:-3]
    return "." + suffix if suffix else ""


# --- Discovery --------------------------------------------------------------


def discover(errors: BuildErrors) -> tuple[list[Preset], dict[str, str]]:
    """Walk examples/ and return (presets, aliases).

    ``aliases`` maps ``preset_name`` → latest versioned name.
    Enforces global uniqueness of ``preset_name`` across the whole tree.
    """
    presets: list[Preset] = []
    seen_preset_names: dict[str, Path] = {}
    latest_version: dict[str, int] = {}
    latest_name: dict[str, str] = {}

    for gateway_dir in sorted(p for p in EXAMPLES_DIR.iterdir() if p.is_dir()):
        for family_dir in sorted(p for p in gateway_dir.iterdir() if p.is_dir()):
            family_presets = _load_family(gateway_dir, family_dir, errors)
            if not family_presets:
                continue

            pname = family_presets[0].preset_name
            if pname in seen_preset_names:
                errors.add(
                    family_dir,
                    f"duplicate preset_name {pname!r} (also declared at "
                    f"{seen_preset_names[pname].relative_to(ROOT)})",
                )
                continue
            seen_preset_names[pname] = family_dir

            for preset in family_presets:
                presets.append(preset)
                if preset.version > latest_version.get(preset.preset_name, 0):
                    latest_version[preset.preset_name] = preset.version
                    latest_name[preset.preset_name] = preset.name

    presets.sort(key=lambda p: (p.preset_name, p.version))
    aliases = dict(sorted(latest_name.items()))
    return presets, aliases


def _load_family(gateway_dir: Path, family_dir: Path, errors: BuildErrors) -> list[Preset]:
    readme_path = family_dir / "README.md"
    if not readme_path.is_file():
        errors.add(family_dir, "missing README.md (required metadata + description)")
        return []

    front = parse_front_matter(readme_path, errors)
    if front is None:
        return []

    # Schema: required fields present, no unknown keys.
    missing = [f for f in REQUIRED_FIELDS if f not in front]
    if missing:
        errors.add(readme_path, f"missing required front-matter field(s): {missing}")
        return []

    allowed = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    unknown = set(front) - allowed
    if unknown:
        errors.add(
            readme_path,
            f"unknown front-matter field(s): {sorted(unknown)}. Allowed: {sorted(allowed)}",
        )
        return []

    preset_name = str(front["preset_name"])
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", preset_name):
        errors.add(
            readme_path,
            f"preset_name {preset_name!r} must be a Python-style identifier "
            "(letters, digits, underscore; cannot start with a digit)",
        )
        return []
    if re.search(r"_v\d+$", preset_name):
        errors.add(
            readme_path,
            f"preset_name {preset_name!r} must not end with '_v<N>' — the version "
            "suffix is appended automatically",
        )
        return []

    mime_type = str(front["mime_type"])
    expected_exts = MIME_EXTENSIONS.get(mime_type)
    if expected_exts is None:
        errors.add(readme_path, f"unknown mime_type {mime_type!r}. Add it to MIME_EXTENSIONS in tools/build.py.")
        return []

    file_field = str(front["file"])
    stem, suffix = split_file_field(file_field)
    if not suffix:
        errors.add(readme_path, f"'file' field {file_field!r} must include an extension")
        return []
    ext = logical_extension(suffix)
    if ext not in expected_exts:
        errors.add(
            readme_path,
            f"'file' extension {ext!r} does not match mime_type {mime_type!r} "
            f"(expected one of {sorted(expected_exts)})",
        )
        return []

    # Discover versions on disk.
    version_pattern = re.compile(rf"^{re.escape(stem)}-v(\d+)\.{re.escape(suffix)}$")
    content_files = {p.name: p for p in family_dir.iterdir() if p.is_file() and p.name != "README.md"}
    matched: dict[int, Path] = {}
    orphans: list[str] = []
    for name, path in content_files.items():
        m = version_pattern.match(name)
        if m is None:
            orphans.append(name)
            continue
        v = int(m.group(1))
        if v in matched:
            errors.add(
                family_dir,
                f"duplicate version v={v} matches both {matched[v].name!r} and {name!r}",
            )
            continue
        matched[v] = path

    if orphans:
        errors.add(
            family_dir,
            f"file(s) do not match version pattern '{stem}-v<N>.{suffix}': {sorted(orphans)}. "
            "Rename, delete, or adjust the 'file' field.",
        )
        # Keep going — we still want to report other issues.

    if not matched:
        errors.add(
            family_dir,
            f"no files matching '{stem}-v<N>.{suffix}' found. "
            "Add at least one versioned file (e.g. '{stem}-v1.{suffix}').".format(stem=stem, suffix=suffix),
        )
        return []

    description = str(front["description"])
    is_active = bool(front.get("is_active", OPTIONAL_FIELDS["is_active"]))
    is_public = bool(front.get("is_public", OPTIONAL_FIELDS["is_public"]))
    meta = dict(front.get("meta", {}))

    parameters = _parse_parameters(readme_path, front, errors)
    if parameters is None:
        return []

    gateway = gateway_dir.name
    family_slug = family_dir.name

    # Validate ${__name__} references in each version's body file.
    # Build-time check catches typos before they ship — runtime callers
    # of file_preset() will also error on unknown names, but earlier is
    # better.
    declared_names = set(parameters)
    for v in sorted(matched):
        file_path = matched[v]
        body = file_path.read_text(encoding="utf-8")
        used = set(PARAM_REFERENCE_RE.findall(body))
        unknown = used - declared_names
        if unknown:
            errors.add(
                file_path,
                f"references undeclared parameter(s) {sorted(unknown)!r}. "
                f"Declare in README front-matter under "
                f"``parameters = {{ ... }}`` or remove the reference. "
                f"Currently declared: {sorted(declared_names) or 'none'}.",
            )

    out: list[Preset] = []
    for v in sorted(matched):
        file_path = matched[v]
        out.append(
            Preset(
                name=f"{preset_name}_v{v}",
                preset_name=preset_name,
                gateway=gateway,
                family_slug=family_slug,
                version=v,
                category=str(front["category"]),
                mime_type=mime_type,
                description=description,
                is_active=is_active,
                is_public=is_public,
                meta=meta,
                parameters=parameters,
                example_file=str(file_path.relative_to(EXAMPLES_DIR).as_posix()),
                source_readme=str(readme_path.relative_to(EXAMPLES_DIR).as_posix()),
            )
        )
    return out


def _parse_parameters(
    readme_path: Path,
    front: dict[str, Any],
    errors: BuildErrors,
) -> dict[str, str] | None:
    """Validate and normalise the ``parameters`` front-matter table.

    Returns the parsed map ``{name: default}`` (string defaults only),
    or ``None`` if a structural error was reported (caller should skip
    the family).  Empty / missing front-matter table → empty dict, which
    is the no-parameters case used by every existing preset.
    """
    raw = front.get("parameters", OPTIONAL_FIELDS["parameters"])
    if not isinstance(raw, dict):
        errors.add(
            readme_path,
            f"'parameters' front-matter must be a TOML table "
            f"(got {type(raw).__name__})",
        )
        return None

    parsed: dict[str, str] = {}
    for name, default in raw.items():
        if not isinstance(name, str) or not PARAM_NAME_RE.match(name):
            errors.add(
                readme_path,
                f"parameter name {name!r} must be a Python-style "
                "identifier (letters / digits / underscore; no leading digit)",
            )
            return None
        if not isinstance(default, str):
            # Per-design: every parameter has a string default.  Numeric
            # / bool / list defaults get added later if a real use case
            # appears; today's only consumer (URL-fragment substitution)
            # is purely textual.
            errors.add(
                readme_path,
                f"parameter {name!r} default must be a string "
                f"(got {type(default).__name__}: {default!r}). "
                "Quote it as TOML \"...\" if needed.",
            )
            return None
        parsed[name] = default
    return parsed


# --- Rendering --------------------------------------------------------------


def render_manifest_json(presets: list[Preset], aliases: dict[str, str]) -> str:
    data = {
        "version": MANIFEST_VERSION,
        "presets": {p.name: p.to_manifest_entry() for p in presets},
        "aliases": dict(aliases),
    }
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def render_manifest_md(presets: list[Preset], aliases: dict[str, str]) -> str:
    lines: list[str] = [
        "# Preset roster",
        "",
        "This file is generated by `tools/build.py`. Do not edit by hand.",
        "",
        f"Schema version: `{MANIFEST_VERSION}`. "
        f"Preset families: **{len({p.preset_name for p in presets})}**. "
        f"Concrete versions: **{len(presets)}**. "
        f"Aliases: **{len(aliases)}**.",
        "",
        "## Concrete presets",
        "",
        "| Preset | Root name | Version | Category | MIME | Public | Example | Description |",
        "|--------|-----------|---------|----------|------|--------|---------|-------------|",
    ]
    for p in presets:
        lines.append(
            "| `{name}` | `{root}` | v{ver} | `{category}` | `{mime}` | {public} | "
            "[`{file}`](src/unitysvc_data/examples/{file}) | {desc} |".format(
                name=p.name,
                root=p.preset_name,
                ver=p.version,
                category=p.category,
                mime=p.mime_type,
                public="yes" if p.is_public else "no",
                file=p.example_file,
                desc=p.description.replace("|", "\\|"),
            )
        )
    lines += ["", "## Aliases (latest-version shortcuts)", ""]
    if aliases:
        lines += [
            "| Alias | Resolves to |",
            "|-------|-------------|",
        ]
        for a in sorted(aliases):
            lines.append(f"| `{a}` | `{aliases[a]}` |")
    else:
        lines.append("_No aliases defined._")
    lines += [
        "",
        "Each family's `README.md` has the front-matter metadata plus prose "
        "describing the example and any per-version differences.",
        "",
    ]
    return "\n".join(lines)


# --- Entry point ------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate only. Exit non-zero on validation errors or if committed outputs are stale.",
    )
    args = parser.parse_args(argv)

    errors = BuildErrors()
    presets, aliases = discover(errors)

    if errors:
        print(f"{len(errors.messages)} validation error(s):", file=sys.stderr)
        for msg in errors.messages:
            print(f"  - {msg}", file=sys.stderr)
        return 1

    manifest_json = render_manifest_json(presets, aliases)
    manifest_md = render_manifest_md(presets, aliases)

    if args.check:
        stale: list[str] = []
        if not MANIFEST_JSON.exists() or MANIFEST_JSON.read_text(encoding="utf-8") != manifest_json:
            stale.append(str(MANIFEST_JSON.relative_to(ROOT)))
        if not MANIFEST_MD.exists() or MANIFEST_MD.read_text(encoding="utf-8") != manifest_md:
            stale.append(str(MANIFEST_MD.relative_to(ROOT)))
        if stale:
            print("Committed outputs are stale:", file=sys.stderr)
            for path in stale:
                print(f"  - {path}", file=sys.stderr)
            print("Run `python tools/build.py` and commit the updated files.", file=sys.stderr)
            return 1
        print(f"{len(presets)} preset(s), {len(aliases)} alias(es); outputs up to date.")
        return 0

    MANIFEST_JSON.write_text(manifest_json, encoding="utf-8")
    MANIFEST_MD.write_text(manifest_md, encoding="utf-8")
    print(
        f"Wrote {MANIFEST_JSON.relative_to(ROOT)} and {MANIFEST_MD.relative_to(ROOT)} "
        f"({len(presets)} preset(s), {len(aliases)} alias(es))."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
