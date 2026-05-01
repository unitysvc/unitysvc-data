# Changelog

All notable changes to `unitysvc-data` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to semantic versioning — minor bumps for new
presets or new versions of existing presets, patch bumps for
non-preset fixes (build script, tests, docs), major bumps only to
remove a previously-published `_vN` preset (should be vanishingly
rare).

## [Unreleased]

## [0.1.10] — LLM connectivity presets + SMTP code-example preset

### Added

- `llm_connectivity_v1` — bash connectivity smoke test for OpenAI-compatible
  LLM services: POSTs a one-token chat completion against
  `{{ routing_key.model }}` and asserts the gateway returned a real `choices`
  array. A step deeper than `api_connectivity` — verifies the model path works,
  not just that the URL responds.
- `llm_connectivity_anthropic_v1` — companion connectivity preset for
  Anthropic-protocol services: POSTs to `/v1/messages`, uses `x-api-key`
  header, sends `anthropic-version: 2023-06-01`, and asserts a `content` array.
- `smtp_code_example_v1` — customer-facing Python send-email smoke test for
  SMTP services (BYOK relay, multi-enrollment relay, mailpit-backed test
  gateway). Dual-mode: local-testing mode inlines seller credentials; gateway
  mode reads `service_base_url` + `UNITYSVC_API_KEY` from env.
- Version-less aliases: `llm_connectivity`, `llm_connectivity_anthropic`,
  `smtp_code_example`.

## [0.1.4] — `@preset` decorator for dynamic discovery

### Added

- ``@preset`` decorator (imported from ``unitysvc_data``) that
  registers the decorated function under its ``__name__`` in a
  module-level ``PRESET_FNS`` mapping. The wrapper built by the
  decorator also unpacks the seller-facing flat sentinel form
  ``{"name": "<preset>", <override>: ...}`` into ``fn(name, **overrides)``
  before calling, so individual preset functions no longer need to
  handle that shape.
- ``PRESET_FNS`` dict exported from the top-level ``unitysvc_data``
  package. Downstream tools (notably ``unitysvc-core``'s
  ``load_data_file``) enumerate this registry to discover every
  sentinel key at runtime — adding a new preset type in future
  versions is a one-line decorator addition in this package, no
  change needed in any consumer.

### Changed

- ``doc_preset`` and ``file_preset`` are now decorated with
  ``@preset``. Their public signatures are unchanged, so programmatic
  callers are unaffected.

## [0.1.3] — absorb common meta overrides into the S3 preset defaults

### Changed

- `s3_connectivity_v1.meta` — added `requirements = ["boto3"]`. The
  script requires boto3 to run, so every listing that embedded this
  preset was repeating the same override.
- `s3_code_example_v1.meta` — now defaults to
  `{ output_contains = "connectivity ok", requirements = ["boto3"] }`.
  Same reasoning: the bundled example prints `connectivity ok` on
  success and requires boto3.

Seller listings that used these presets and had been supplying those
keys as `$with` overrides can drop the overrides entirely now —
`{"$doc_preset": "s3_connectivity"}` / `{"$doc_preset": "s3_code_example"}`
produce the same fully-populated record without any boilerplate.

### Append-only caveat

This release mutates published v1 metadata — normally append-only.
The change is purely additive (new keys alongside the existing
`output_contains`), so any listing that was already setting
`requirements` explicitly continues to work via the flat-form
override's deep-merge of `meta`.

## [0.1.2] — align preset categories with `DocumentCategoryEnum`

### Fixed

- `s3_code_example_v1.category` — `usage_example` → `code_example`
  (matches `unitysvc_core.models.base.DocumentCategoryEnum`; the old
  value was not a valid enum member and would have been rejected by
  the backend schema validator).
- `s3_description_v1.category` — `description` → `getting_started`
  (same reason; `getting_started` is how the upstream template repo
  catalogued the S3 overview markdown).

### Note on append-only discipline

v1 preset metadata is normally append-only — this release bends that
rule because v1 as published was unusable (the categories were
invalid). If you already reference these presets with overrides,
review that nothing assumed the old category string.

## [0.1.1] — Python 3.11 import fix

### Fixed

- Package failed to import on Python 3.11: `presets.py` used
  `importlib.resources.files(__name__)` with the module-level
  `__name__` (`"unitysvc_data.presets"`), which 3.11's
  `importlib.resources` rejects as "not a package." Switched both
  `_EXAMPLES_ROOT` and `_load_manifest` to `__package__`
  (`"unitysvc_data"`), which works uniformly on 3.11 and 3.12.

v0.1.0 remains on PyPI but is effectively Python-3.12-only. Users
on 3.11 should pin to `>=0.1.1`.

## [0.1.0] — initial release

Six preset families, one version each. Manifest schema version `1`.

### Added

- Preset families and their `v1` entries:
  - `api_connectivity_v1` — generic HTTP connectivity smoke test (bash).
  - `s3_connectivity_v1` — S3 credential verification (python).
  - `s3_code_example_v1` — list objects via `boto3` (python).
  - `s3_description_v1` — S3 gateway service overview (markdown).
  - `smtp_connectivity_v1` — SMTP banner check (bash).
  - `llm_request_template_v1` — OpenAI-compatible chat completion body (json).
- Version-less aliases for every family
  (e.g. `s3_connectivity` → `s3_connectivity_v1`).
- `doc_preset(source, **overrides)` / `file_preset(source)` /
  `list_presets()` Python primitives.
- `usvc_data` CLI with `list`, `doc-preset`, `file-preset` subcommands.
- `register_jinja_globals(env)` for generated-repo templates that want
  to call preset factories as Jinja functions.
- `tools/build.py` — regenerates `_manifest.json` and `MANIFEST.md`
  from per-family `README.md` front-matter; validates globally-unique
  `preset_name`s, filename conventions, and mime-type / extension
  agreement.
- CI: manifest-freshness check, ruff, pytest on Python 3.11 and 3.12,
  wheel-content smoke test.
- PyPI trusted publishing on GitHub Release via `publish.yml`.
