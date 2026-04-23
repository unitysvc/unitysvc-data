# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode (requires uv)
uv pip install -e '.[test]'

# Run all tests
pytest -q

# Run a single test file
pytest tests/test_presets.py -q

# Lint
ruff check src/ tests/ tools/

# Regenerate _manifest.json and MANIFEST.md after adding/modifying example files
python tools/build.py

# Validate manifest is up to date (used in CI)
python tools/build.py --check
```

## Architecture

This is a **data-first Python package** that ships versioned example files and preset factories for UnitySVC integrations. The primary consumer is `unitysvc-sellers`, which uses this package to expand `$preset` sentinels in `listing.json` into full document records at upload time.

### Core flow

1. Example files live under `src/unitysvc_data/examples/<gateway>/<family>/`
2. Each family has a `README.md` with TOML front-matter (metadata) and a prose description
3. Versioned files follow the pattern `<stem>-v<N>.<ext>[.j2]` (Jinja2 templates get `.j2` appended)
4. `python tools/build.py` discovers all versions, validates structure, and writes `_manifest.json` + `MANIFEST.md`
5. At runtime, `doc_preset(source, **overrides)` returns a full document record; `file_preset(source)` returns raw file content

### Key modules

- **`presets.py`** — `doc_preset()`, `file_preset()`, `PRESETS` dict, `ALIASES` dict; loads `_manifest.json` at import time for O(1) lookups
- **`_registry.py`** — `@preset` decorator and `PRESET_FNS` registry; used by `unitysvc-core` to discover preset function types dynamically
- **`cli.py`** — `usvc_data` console script; subcommands: `list`, `info`, `doc-preset`, `file-preset`
- **`tools/build.py`** — manifest generator; validates TOML front-matter, discovers versioned files, enforces uniqueness

### Preset naming and versioning

- **Versioned name**: `s3_connectivity_v1` — pinned to a specific version
- **Alias**: `s3_connectivity` — always resolves to the latest version
- Versions are **append-only**: never modify or delete existing versioned files
- Only `description`, `is_public`, `is_active`, and `meta` fields can be overridden via `$with`; `category`, `mime_type`, and `file_path` are immutable

### Two calling conventions

Both are handled transparently by `doc_preset` and `file_preset`:
1. **Bare string**: `"s3_connectivity"` or `"s3_connectivity_v1"`
2. **JSON sentinel**: `{"$preset": "s3_connectivity", "$with": {"description": "custom"}}`

### Adding a new preset

1. Create `src/unitysvc_data/examples/<gateway>/<family>/README.md` with TOML front-matter (`preset_name`, `category`, `mime_type`, `file`, `description`)
2. Add the versioned file: `src/unitysvc_data/examples/<gateway>/<family>/<stem>-v1.<ext>`
3. Run `python tools/build.py` to regenerate the manifest
4. CI will fail if `_manifest.json` is stale

### Important constraints

- Zero runtime dependencies — stdlib only
- Python 3.11+ required
- `ruff` line-length is 120
- CI validates manifest freshness, runs ruff and pytest on 3.11 and 3.12, and checks that the built wheel includes example files and the manifest
