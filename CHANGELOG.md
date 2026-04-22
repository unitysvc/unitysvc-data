# Changelog

All notable changes to `unitysvc-data` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to semantic versioning — minor bumps for new
presets or new versions of existing presets, patch bumps for
non-preset fixes (build script, tests, docs), major bumps only to
remove a previously-published `_vN` preset (should be vanishingly
rare).

## [Unreleased]

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
