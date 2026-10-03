#!/usr/bin/env python3
"""Build the preset manifest and human-readable roster from examples/.

Layout the script expects
-------------------------

Each preset family lives in
``src/unitysvc_data/examples/<gateway>/<family>/`` and contains:

- ``README.md`` with TOML front-matter delimited by ``+++`` lines. The
  front-matter supplies metadata shared by all presets in the directory;
  per-version prose goes underneath the front-matter.
- Versioned files named ``<stem>-v<N>.<suffix>`` or
  ``<stem>-<variant>-v<N>.<suffix>``, where the stem and suffix come
  from the ``file`` front-matter field.

  ``file = "code-example.py.j2"`` discovers:

  - ``code-example-v1.py.j2`` → registered as ``<preset_name>_v1``
  - ``code-example-discord-v1.py.j2`` → ``<preset_name>_discord_v1``
  - ``code-example-slack-v1.py.j2``   → ``<preset_name>_slack_v1``

  Each variant becomes its own independent preset family, inheriting
  all metadata (category, mime_type, is_active, …) from the shared
  README.md. The variant slug is appended to the base ``preset_name``
  with an underscore: ``<preset_name>_<variant>``.

  Variant slugs must be lowercase ASCII letters and digits
  (``[a-z][a-z0-9]*``).  Hyphens in the file name are converted to
  underscores in the preset name
  (``code-example-msteams-webhook-v1.py.j2`` →
  ``<preset_name>_msteams_webhook_v1``).

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

A directory may contain only variant files (no bare ``<stem>-v<N>``
base file).  The shared README.md is still required in that case.

Request templates
-----------------

A ``category = "request_template"`` JSON file is what the Test Request
playground starts a request from. One document covers ONE capability (its
``applies_to.capability``) and holds one entry per request format::

    [ { "format": "openai",    "body": { ... } },
      { "format": "anthropic", "body": { ... } } ]

The playground reads the FIRST entry naming the format the customer picked, so
``check_request_templates`` fails the build when an entry could never be read:
a repeated format, a missing or unregistered ``format``, a missing ``body``.
Versions that predate the entry list stay as published; the latest version of a
template that names a capability must be one.

An entry may carry a ``path_suffix``, appended to the service's base URL. It is
read off the code example the body came from, and may use the same
``${__version_prefix__}`` placeholder the OpenAI-shaped examples do (declared in
the family's ``parameters``). The check refuses one that would build a request
nothing can send: not a string, not a path, or a placeholder nothing substitutes. An
entry that posts to the bare base URL omits the key rather than writing ``""`` or ``/``.

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
import difflib
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ``classifiers`` is imported from the source tree rather than an installed
# package on purpose. This script GENERATES the manifest that
# ``unitysvc_data.presets`` loads at import time, so it must not require the
# package to be installed to run -- but the classifier registry is pure data
# and reads no manifest, so importing it introduces no bootstrap cycle.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from unitysvc_data import classifiers, titles

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "src" / "unitysvc_data" / "examples"
MANIFEST_JSON = ROOT / "src" / "unitysvc_data" / "_manifest.json"
MANIFEST_MD = ROOT / "MANIFEST.md"
MANIFEST_VERSION = "1"

# Gateways whose presets ``unitysvc_data.presets._select`` fans out over, picking
# every one whose ``applies_to`` admits the service. Every other gateway's presets
# are referenced by name (``$doc_preset: x``), so two of them sharing a selector are
# variants a listing chooses between rather than documents competing for a title.
SELECTED_GATEWAYS = frozenset({"llm"})

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
    # ``applies_to`` states WHEN an example applies, so selection is data
    # rather than pattern-matching on preset names. The axes and every value
    # each one accepts are declared in ``src/unitysvc_data/classifiers.py``,
    # which this script validates against — an unknown key or value fails the
    # build, because an ABSENT key means "no constraint" and so a typo widens
    # the selector instead of narrowing it. The registry also owns the display
    # label each value renders as in a document title.
    #
    #   capability  the platform capability it demonstrates (required for
    #               code examples that a collection should select)
    #   dialect     the request dialect the CALLER writes
    #   upstream    the dialect the service's upstream speaks; differs from
    #               ``dialect`` when the gateway translates
    #   feature     an attribute gate — streaming / tools / vision — that
    #               the service must advertise before the example applies
    # Like ``parameters`` it is build-time metadata and never reaches the
    # document record.
    "applies_to": {},
    # Per-version metadata overrides, e.g.
    #     [versions.v1]
    #     meta = { requirements = ["requests"] }
    # ``meta`` in the front-matter is shared by every version in the
    # directory. Keys here are merged over the shared meta for that version
    # only; a null value drops the key.
    "versions": {},
}

# Pattern declared parameter names must match (Python-identifier-like).
PARAM_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# Parameter names that would collide with metadata override keys.  The
# seller-facing flat form (``{"$doc_preset": {"name": "x", "<key>": ...}}``)
# auto-discriminates by checking each key against the preset's declared
# parameters; if a parameter shared a name with one of these metadata
# fields, the discrimination would be ambiguous.  Forbid the collision
# at build time so author intent is unambiguous.
PARAM_NAME_FORBIDDEN = frozenset({"description", "is_public", "is_active", "meta"})

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
    applies_to: dict[str, Any]     # capability / dialect / upstream / feature
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
            "applies_to": self.applies_to,
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


def _meta_for(shared: dict[str, Any], overrides: dict[str, Any], version: int) -> dict[str, Any]:
    """Shared meta with this version's overrides applied.

    A null value removes the key, which is how an older version opts out of
    something a later one declares.
    """
    over = (overrides.get(f"v{version}") or {}).get("meta")
    if not over:
        return dict(shared)
    merged = {**shared, **over}
    return {k: v for k, v in merged.items() if v not in (None, "")}


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
    suffix = suffix.removesuffix(".j2")
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
            all_families = _load_families(gateway_dir, family_dir, errors)

            for family_presets in all_families:
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


def _load_families(gateway_dir: Path, family_dir: Path, errors: BuildErrors) -> list[list[Preset]]:
    """Load all preset families from *family_dir*.

    A directory normally contains exactly one family (the base family whose
    preset_name is declared in README.md).  When the directory also contains
    *variant* files — named ``<stem>-<variant>-v<N>.<suffix>`` — each distinct
    variant becomes an additional family whose preset_name is
    ``<base_preset_name>_<variant_slug>`` (hyphens replaced with underscores).
    Variant families inherit all metadata from the README except preset_name.

    Returns a list of families, where each family is a list of Preset objects
    (one per version).  Returns ``[[]]`` on fatal error so callers can detect
    the failure without crashing.
    """
    return _load_family(gateway_dir, family_dir, errors)


def _load_family(gateway_dir: Path, family_dir: Path, errors: BuildErrors) -> list[list[Preset]]:
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

    # ``applies_to`` selects which services get this example, and an ABSENT key
    # means "no constraint" -- so a misspelled axis or value does not narrow the
    # selector, it silently widens it. Validate against the registry, which also
    # owns the display label each value renders as in a title.
    applies_to = front.get("applies_to") or {}
    if not isinstance(applies_to, dict):
        errors.add(readme_path, f"applies_to must be a table, got {type(applies_to).__name__}")
        return []
    for problem in classifiers.validate(applies_to):
        errors.add(readme_path, problem)
    if classifiers.validate(applies_to):
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
    # Variant pattern: <stem>-<variant>-v<N>.<suffix>
    # Variant slug: lowercase letters/digits, segments separated by hyphens.
    variant_pattern = re.compile(
        rf"^{re.escape(stem)}-([a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)*)-v(\d+)\.{re.escape(suffix)}$"
    )
    content_files = {p.name: p for p in family_dir.iterdir() if p.is_file() and p.name != "README.md"}
    matched: dict[int, Path] = {}
    # variant_files: variant_slug -> {version -> path}
    variant_files: dict[str, dict[int, Path]] = {}
    orphans: list[str] = []
    for name, path in content_files.items():
        m = version_pattern.match(name)
        if m is not None:
            v = int(m.group(1))
            if v in matched:
                errors.add(
                    family_dir,
                    f"duplicate version v={v} matches both {matched[v].name!r} and {name!r}",
                )
                continue
            matched[v] = path
            continue
        vm = variant_pattern.match(name)
        if vm is not None:
            variant_slug = vm.group(1)
            v = int(vm.group(2))
            vdict = variant_files.setdefault(variant_slug, {})
            if v in vdict:
                errors.add(
                    family_dir,
                    f"duplicate version v={v} for variant {variant_slug!r}: "
                    f"{vdict[v].name!r} and {name!r}",
                )
                continue
            vdict[v] = path
            continue
        orphans.append(name)

    if orphans:
        errors.add(
            family_dir,
            f"file(s) do not match version pattern '{stem}-v<N>.{suffix}' or "
            f"variant pattern '{stem}-<variant>-v<N>.{suffix}': {sorted(orphans)}. "
            "Rename, delete, or adjust the 'file' field.",
        )
        # Keep going — we still want to report other issues.

    if not matched and not variant_files:
        errors.add(
            family_dir,
            f"no files matching '{stem}-v<N>.{suffix}' found. "
            "Add at least one versioned file (e.g. '{stem}-v1.{suffix}').".format(stem=stem, suffix=suffix),
        )
        return [[]]

    description = str(front["description"])
    is_active = bool(front.get("is_active", OPTIONAL_FIELDS["is_active"]))
    is_public = bool(front.get("is_public", OPTIONAL_FIELDS["is_public"]))
    meta = dict(front.get("meta", {}))
    version_overrides = dict(front.get("versions", {}))

    parameters = _parse_parameters(readme_path, front, errors)
    if parameters is None:
        return [[]]

    gateway = gateway_dir.name
    family_slug = family_dir.name
    category = str(front["category"])

    # ``${__name__}`` references in the body that aren't declared in
    # front-matter ``parameters`` are intentionally left alone at
    # substitution time, not flagged as build errors.  The strict-check
    # alternative was rejected because it forbade legitimate uses
    # (literal documentation strings, typos in test fixtures, params
    # staged in a future version of the body before being declared).
    # Substitution is best-effort: declared placeholders get replaced,
    # everything else passes through verbatim.

    all_families: list[list[Preset]] = []

    # Base family (files matching <stem>-v<N>.<suffix>).
    if matched:
        base_presets: list[Preset] = []
        for v in sorted(matched):
            file_path = matched[v]
            base_presets.append(
                Preset(
                    name=f"{preset_name}_v{v}",
                    preset_name=preset_name,
                    gateway=gateway,
                    family_slug=family_slug,
                    version=v,
                    category=category,
                    mime_type=mime_type,
                    description=description,
                    is_active=is_active,
                    is_public=is_public,
                    meta=_meta_for(meta, version_overrides, v),
                    parameters=parameters,
                    applies_to=dict(front.get("applies_to", {})),
                    example_file=str(file_path.relative_to(EXAMPLES_DIR).as_posix()),
                    source_readme=str(readme_path.relative_to(EXAMPLES_DIR).as_posix()),
                )
            )
        all_families.append(base_presets)

    # Variant families (files matching <stem>-<variant>-v<N>.<suffix>).
    for variant_slug in sorted(variant_files):
        vdict = variant_files[variant_slug]
        variant_preset_name = f"{preset_name}_{variant_slug.replace('-', '_')}"
        variant_presets: list[Preset] = []
        for v in sorted(vdict):
            file_path = vdict[v]
            variant_presets.append(
                Preset(
                    name=f"{variant_preset_name}_v{v}",
                    preset_name=variant_preset_name,
                    gateway=gateway,
                    family_slug=family_slug,
                    version=v,
                    category=category,
                    mime_type=mime_type,
                    description=description,
                    is_active=is_active,
                    is_public=is_public,
                    meta=_meta_for(meta, version_overrides, v),
                    parameters=parameters,
                    applies_to=dict(front.get("applies_to", {})),
                    example_file=str(file_path.relative_to(EXAMPLES_DIR).as_posix()),
                    source_readme=str(readme_path.relative_to(EXAMPLES_DIR).as_posix()),
                )
            )
        all_families.append(variant_presets)

    return all_families


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
        if name in PARAM_NAME_FORBIDDEN:
            errors.add(
                readme_path,
                f"parameter name {name!r} collides with a metadata "
                f"override key.  The flat-form listing dispatch "
                f"(``{{\"$doc_preset\": {{\"name\": \"...\", "
                f"\"{name}\": ...}}}}``) discriminates params from "
                f"overrides by name, so parameters cannot be one of "
                f"{sorted(PARAM_NAME_FORBIDDEN)!r}.  Pick a different "
                "parameter name.",
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


def check_titles(presets: list[Preset], errors: BuildErrors) -> None:
    """No two examples that can meet on one service may render the same title.

    A title is a document's KEY -- the backend upserts on
    ``(entity_id, context_type, title)`` -- so a clash does not fail, it
    overwrites, and the losing example is gone with no signal. That is how an
    omni model once shipped one of its three capabilities' examples and
    silently dropped the other two.

    Two checks, deliberately split:

    * ``classifiers.check_registry()`` is stated over the DECLARED values, so a
      value added with a missing or duplicate label fails before any example
      adopts it.
    * the loop below is stated over the CORPUS, because whether a clash is
      reachable depends on which combinations examples actually declare -- the
      registry permits pairs that no example realises.

    Two examples can meet when they agree on every axis that does NOT co-occur
    (today just ``upstream``: one collection is built with one upstream, so
    examples declaring different ones are never selected together). Versions of
    one preset share a title on purpose and are compared once, by name.

    Two PRESETS with identical ``applies_to`` are the extreme case of meeting --
    nothing separates them, so both are selected for every service that gets
    either -- and in a gateway ``_select`` fans out over (``SELECTED_GATEWAYS``)
    they are a clash like any other: the later name replaces the earlier. This used
    to be skipped as "same selector: one document", which is right for versions and
    wrong for presets, and a variant file makes it easy to do by accident because it
    inherits its README's ``applies_to`` wholesale. Elsewhere sharing a selector is
    how per-channel variants are written, so it stays allowed there.
    """
    for problem in classifiers.check_registry():
        errors.add(Path("src/unitysvc_data/classifiers.py"), problem)

    # One entry per preset_name: versions share applies_to and a title, which
    # is correct -- same document, newer content.
    by_name: dict[str, Preset] = {}
    for preset in presets:
        by_name.setdefault(preset.preset_name, preset)

    # Scoped per gateway family. A service's documents come from ONE family --
    # `presets._select` only considers `llm_*`, and the other families are
    # referenced by name -- so `api_connectivity` and `llm_connectivity` both
    # being "Connectivity test" is not a clash: they never meet.
    grouped: dict[tuple[str, str], list[str]] = {}
    for name, preset in by_name.items():
        rendered = titles.title(preset.to_manifest_entry(), preset.applies_to)
        grouped.setdefault((preset.gateway, rendered), []).append(name)

    for (gateway, title_text), names in sorted(grouped.items()):
        if len(names) < 2:
            continue
        ordered = sorted(names)
        for i, a in enumerate(ordered):
            for b in ordered[i + 1 :]:
                spec_a, spec_b = by_name[a].applies_to, by_name[b].applies_to
                if spec_a == spec_b:
                    if gateway not in SELECTED_GATEWAYS:
                        continue  # named variants: the listing picks one by name
                    errors.add(
                        Path(EXAMPLES_DIR.name) / by_name[a].source_readme,
                        f"{a} and {b} both render the title {title_text!r} and declare the "
                        f"same applies_to ({spec_a or 'none'}), so both are selected for the "
                        f"same service and the later name silently replaces the earlier. "
                        f"Give one a different selector, or make them versions of one preset. "
                        f"(A <stem>-<variant>-v<N> file is its own preset and inherits its "
                        f"README's applies_to wholesale.)",
                    )
                    continue
                axes = set(spec_a) | set(spec_b)
                exclusive = any(
                    not classifiers.co_occurs(axis)
                    and axis in spec_a
                    and axis in spec_b
                    and spec_a[axis] != spec_b[axis]
                    for axis in axes
                )
                if exclusive:
                    continue
                differ = sorted(k for k in axes if spec_a.get(k) != spec_b.get(k))
                errors.add(
                    Path(EXAMPLES_DIR.name) / by_name[a].source_readme,
                    f"{a} and {b} both render the title {title_text!r} and can be "
                    f"selected for the same service, so one would overwrite the "
                    f"other. They differ on {differ} -- give that axis's values "
                    f"distinct labels in src/unitysvc_data/classifiers.py.",
                )


def check_request_templates(presets: list[Preset], errors: BuildErrors) -> None:
    """Every entry of a request template must be reachable by the format it names.

    The playground (``frontend/lib/requestTemplates.ts``) picks a template by the
    capability its ``applies_to`` names, then the FIRST entry whose ``format``
    equals the one the customer selected. A template is therefore a function of
    ``(capability, format)``, and anything that breaks that fails nowhere else --
    the customer simply never sees the request the author wrote:

    * a second entry for one ``(capability, format)`` is never read;
    * an entry with no usable ``format`` can never match, and one with no
      ``body`` is skipped;
    * a ``format`` no service can select is the same dead entry with a typo, so
      it is checked against the registered dialects, with a near-miss hint, the
      way ``applies_to`` is.

    Within one document the capability is the document's, so the uniqueness key
    ``(capability, format)`` reduces to ``format``; it is named in the message
    because that is the pair the reader's contract is stated over.

    Every version is read, not only the latest: ``$doc_preset: x_v1`` still
    resolves, so a duplicate in a pinned version is served too. Versions that
    predate the entry list -- a flat body, or a dict keyed by format -- are
    append-only history and are skipped, EXCEPT that the latest version of a
    template that names a capability must be an entry list. That is what the
    alias hands every listing, and the page's reader for the old shape is marked
    deletable only once nothing publishes it.

    ``path_suffix``, when an entry has one, must be a path the playground can
    append to a service's base URL (see :func:`_path_suffix_problem`). Other keys
    inside an entry beyond ``format`` and ``body`` are ignored on purpose: the
    reader ignores them, so ``content_type`` can ship ahead of any page that
    reads it.
    """
    latest: dict[str, int] = {}
    for preset in presets:
        latest[preset.preset_name] = max(latest.get(preset.preset_name, 0), preset.version)

    for preset in presets:
        if preset.category != "request_template" or preset.mime_type != "json":
            continue
        path = EXAMPLES_DIR / preset.example_file
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.add(path, f"not valid JSON: {exc}")
            continue
        capability = preset.applies_to.get("capability")
        if isinstance(document, list):
            _check_template_entries(path, document, capability, preset.parameters, errors)
        elif capability and preset.version == latest[preset.preset_name]:
            errors.add(
                path,
                f"the latest version of a request template for capability {capability!r} "
                f"must be an entry list ([{{\"format\": ..., \"body\": ...}}, ...]), not "
                f"{type(document).__name__}: this is what the alias gives every listing, and "
                f"the dict shape is the legacy one the playground is waiting to drop. "
                f"Publish it as a new version.",
            )


def _check_template_entries(
    path: Path,
    entries: list[Any],
    capability: str | None,
    parameters: dict[str, str],
    errors: BuildErrors,
) -> None:
    """The entries of one list-shaped template; see :func:`check_request_templates`."""
    if not entries:
        errors.add(path, "has no entries, so it offers no request for any format")
        return
    scope = f" for capability {capability!r}" if capability else ""
    first_seen: dict[str, int] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.add(path, f"entry {index} is not an object, so the playground skips it")
            continue
        raw = entry.get("format")
        fmt = raw.strip() if isinstance(raw, str) else ""
        if not fmt:
            errors.add(
                path,
                f"entry {index} has no usable `format` (got {raw!r}), so it can never match "
                f"the format a customer selects",
            )
            continue
        if entry.get("body") is None:
            errors.add(path, f"entry {index} ({fmt!r}) has no `body`, so the playground skips it")
            continue
        if fmt not in classifiers.DIALECTS:
            hint = difflib.get_close_matches(fmt, classifiers.DIALECTS, n=1)
            suffix = f" Did you mean {hint[0]!r}?" if hint else ""
            errors.add(
                path,
                f"entry {index} names format {fmt!r}, which is not in classifiers.DIALECTS "
                f"(src/unitysvc_data/classifiers.py). Register it there or fix the spelling -- "
                f"an entry for a format nobody has declared is one no service can select.{suffix}",
            )
        if "path_suffix" in entry and (problem := _path_suffix_problem(entry["path_suffix"], parameters)):
            errors.add(path, f"entry {index} ({fmt!r}): {problem}")
        if fmt in first_seen:
            errors.add(
                path,
                f"entries {first_seen[fmt]} and {index} both name format {fmt!r}{scope}. The "
                f"playground reads the first, so entry {index} is unreachable.",
            )
        else:
            first_seen[fmt] = index


def _path_suffix_problem(value: Any, parameters: dict[str, str]) -> str | None:
    """Why a ``path_suffix`` would build a request nothing can send, or ``None``.

    The playground appends it to the service's base URL. Every mistake caught here
    yields a request that looks plausible and fails, which is the failure the key
    exists to end:

    * not a string;
    * not a path -- an absolute URL, a host-rooted ``//host``, or anything with
      whitespace, would be appended to a base URL that already has a host;
    * a placeholder nothing substitutes. ``${__name__}`` is replaced from the family's
      ``parameters`` when the document is built, so an undeclared one survives into
      the request; and a ``{{ ... }}`` expression is never rendered at all, because a
      template is plain JSON and not a ``.j2``. Both would be sent literally.

    The path is judged AFTER the declared defaults are substituted, so what is checked is
    the one a service that sets nothing of its own would get. It must then start with ``/``.

    An entry that posts to the bare base URL -- DashScope's native examples post to the
    service URL itself -- has NO ``path_suffix``; it does not write a value for "nothing".
    The page treats a missing or blank one as absent and falls back, so a blank value says
    nothing a missing key does not, and ``/`` is a different request (it appends a trailing
    slash). Both are refused, with that instruction.
    """
    if not isinstance(value, str):
        return f"path_suffix must be a string, got {type(value).__name__}"
    rendered = value
    for name, default in parameters.items():
        rendered = rendered.replace(f"${{__{name}__}}", default)
    if "${" in rendered or "{{" in rendered:
        return (
            f"path_suffix {value!r} still contains a placeholder once the declared parameters are "
            f"applied. Declare it in the family's `parameters`; a request template is not rendered, "
            f"so anything else is sent literally."
        )
    if rendered.startswith("//") or "://" in rendered:
        return f"path_suffix {value!r} must be a path, not a URL: it is appended to the service's base URL"
    if rendered.strip() in ("", "/"):
        return (
            f"path_suffix {value!r} says nothing: omit the key for an entry that posts to the bare "
            f"base URL. The page treats a blank path_suffix as absent, and '/' would append a "
            f"trailing slash, which is not the same request."
        )
    if any(ch.isspace() for ch in rendered):
        return f"path_suffix {value!r} contains whitespace, so it cannot be a path"
    if not rendered.startswith("/"):
        return f"path_suffix {value!r} must start with '/': it is appended to the service's base URL"
    return None


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
        (f"Schema version: `{MANIFEST_VERSION}`. "
        f"Preset families: **{len({p.preset_name for p in presets})}**. "
        f"Concrete versions: **{len(presets)}**. "
        f"Aliases: **{len(aliases)}**."),
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
        ("Each family's `README.md` has the front-matter metadata plus prose "
        "describing the example and any per-version differences."),
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
    if not errors:
        # Only meaningful once every preset parsed: a half-discovered corpus
        # would report clashes that are really parse failures.
        check_titles(presets, errors)
        check_request_templates(presets, errors)

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
