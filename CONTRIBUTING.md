# Contributing to unitysvc-data

Thanks for contributing an example! This guide walks you through adding a
new preset (or a new version of an existing one) from scratch. The
whole process is designed to be cheap — most presets are 5–20 minutes
of work end-to-end.

If something in this guide is unclear or out of date, file an issue
against the sibling repo that consumes this package:
https://github.com/unitysvc/unitysvc-sellers/issues (tag with
`unitysvc-data`).

---

## TL;DR

Adding a brand-new preset called `<gateway>_<family>` — for example
`s3_multipart_upload`:

```bash
# 1. Create the family directory
mkdir -p src/unitysvc_data/examples/s3/multipart-upload

# 2. Drop your example file with a -v1 suffix
$EDITOR src/unitysvc_data/examples/s3/multipart-upload/multipart-upload-v1.py.j2

# 3. Author the README.md with front-matter + prose
$EDITOR src/unitysvc_data/examples/s3/multipart-upload/README.md

# 4. Regenerate the manifest and the human roster
python tools/build.py

# 5. Run the full verification locally
ruff check src/ tests/ tools/
pytest -q

# 6. Bump pyproject.toml and _version.py (minor bump), commit, PR
```

Adding a **v2** to an existing family is even shorter — see
[Adding a new version](#adding-a-new-version-to-an-existing-family).

---

## Development setup

Prerequisites: Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/unitysvc/unitysvc-data
cd unitysvc-data
uv venv
uv pip install -e '.[test]' jinja2 build
```

Sanity-check the tree:

```bash
python tools/build.py --check     # manifest is up to date
ruff check src/ tests/ tools/
pytest -q
```

All three should pass on a clean checkout.

---

## Adding a new preset family

A **preset family** is a logical example that may have multiple
versions over time. Examples of families: `api_connectivity`,
`s3_code_example`, `llm_request_template`.

### 1. Pick a home

Decide which gateway the example belongs to:

| Gateway      | What it holds                                     |
|--------------|---------------------------------------------------|
| `api/`       | generic HTTP services                             |
| `llm/`       | OpenAI-compatible LLM gateway                     |
| `s3/`        | S3-compatible storage gateway                     |
| `smtp/`      | SMTP relay                                        |

Need a gateway that doesn't exist yet? Just create
`src/unitysvc_data/examples/<new-gateway>/`. Gateways are discovered
automatically — no registration needed.

### 2. Pick a family slug

The directory name and the `preset_name` field work in tandem.

- **Directory name** — lowercase with dashes, describes the example
  (e.g. `multipart-upload`, `connectivity`, `request-template`).
- **`preset_name`** — a Python-style identifier (letters, digits,
  underscores; cannot start with a digit, cannot end with `_v<N>`).
  Convention: `<gateway>_<dir-name-with-underscores>`
  (e.g. `s3_multipart_upload`).

`preset_name` is **globally unique** across the whole tree — the build
fails if two families declare the same one. This is the name sellers
will write in their `$preset` sentinels, so pick something
self-describing.

### 3. Create the directory and the v1 file

```
src/unitysvc_data/examples/<gateway>/<family-slug>/
├── README.md                                       # written in step 4
└── <file-stem>-v1.<extension>[.j2]                 # your example content
```

Rules for the filename:

- Stem + extension are declared by the `file` field in the
  front-matter (step 4). Common convention is to match the directory
  slug (`multipart-upload` → `multipart-upload-v1.py.j2`).
- The `-v1` suffix is mandatory. Future versions become `-v2`, `-v3`,
  etc., in the same directory.
- Use `.j2` for files that need Jinja2 rendering at seller-upload time
  (per-listing context like `{{ interface.base_url }}`). Omit `.j2`
  for fully-static files.

### 4. Author `README.md`

The README is the single source of truth for the family's metadata.
It has two parts:

**Front-matter** (TOML, delimited by `+++`). Required fields:

| Field          | Type    | Example                                          |
|----------------|---------|--------------------------------------------------|
| `preset_name`  | string  | `"s3_multipart_upload"`                          |
| `category`     | string  | `"usage_example"`, `"connectivity_test"`, ...    |
| `mime_type`    | string  | `"python"`, `"bash"`, `"markdown"`, `"json"`, ...|
| `file`         | string  | `"multipart-upload.py.j2"` (no version suffix)   |
| `description`  | string  | A one-line description for the listing document  |

Optional fields (defaults shown):

| Field       | Default  | Purpose                                    |
|-------------|----------|--------------------------------------------|
| `is_active` | `true`   | Document is active on the listing          |
| `is_public` | `false`  | Document is customer-visible               |
| `meta`      | `{}`     | Free-form metadata (e.g. `output_contains`)|

**Prose** (Markdown, below the closing `+++`). What to cover:

1. A one-paragraph summary of what the example does.
2. Any relevant environment variables or template context the example
   reads.
3. Pass/fail criteria if it's a test.
4. A `## Versions` section with a `### v1 — initial release` subsection
   describing what landed in v1.

Minimal template:

```markdown
+++
preset_name = "s3_multipart_upload"
category = "usage_example"
mime_type = "python"
file = "multipart-upload.py.j2"
description = "Upload a large object to S3 using multipart."
is_active = true
is_public = true
+++

# s3 / multipart-upload — multipart S3 upload

Prose description here — what this example does, who it's for, and
why it's in the bundled set.

## Versions

### v1 — initial release

What's in v1.
```

The recognised `mime_type` → file-extension mapping lives in
[`tools/build.py`](tools/build.py) under `MIME_EXTENSIONS`. Adding a
new mime type (e.g. `"rust"` → `{".rs"}`) is a one-line change there.

### 5. Regenerate the manifest

```bash
python tools/build.py
```

This rewrites `src/unitysvc_data/_manifest.json` and the top-level
`MANIFEST.md`. **Commit both** — CI runs `python tools/build.py --check`
and fails on drift.

### 6. Verify locally

```bash
ruff check src/ tests/ tools/
pytest -q
```

`test_manifest_is_up_to_date` will fail if you forgot step 5.

### 7. Bump the package version

Edit `pyproject.toml` and `src/unitysvc_data/_version.py`. Since new
presets are additive, a **minor** bump (e.g. `0.2.0 → 0.3.0`) is right.

### 8. Open the PR

Include in the description:

- The preset name and what it does.
- Any non-obvious decisions (e.g. why this belongs in `s3/` rather
  than `api/`).
- A link to the downstream use case (if relevant).

---

## Adding a new version to an existing family

Example: adding `s3_connectivity_v2`.

1. Drop the new file next to the existing ones:
   ```
   src/unitysvc_data/examples/s3/connectivity/connectivity-v2.py.j2
   ```
   The stem and suffix must match the `file` field in that family's
   `README.md` — you don't edit the front-matter.
2. Add a `### v2 — <short title>` section under `## Versions` in the
   family's `README.md` explaining what changed.
3. `python tools/build.py`
4. `pytest -q`
5. Bump the package version (minor bump).

The version-less alias (`s3_connectivity`) automatically shifts to
point at `s3_connectivity_v2`. Seller data pinned to
`s3_connectivity_v1` keeps the old behaviour; data using the alias
tracks the newest version.

**Existing `-vN` files and their behaviour are append-only.** Never
edit `connectivity-v1.py.j2` or its metadata after it's published —
sellers rely on pinned versions staying byte-identical across
package upgrades. If you need to change v1, the answer is always
"publish v2."

---

## Filename and directory conventions, in one place

| Element              | Rule                                                                 |
|----------------------|----------------------------------------------------------------------|
| Gateway directory    | `src/unitysvc_data/examples/<gateway>/`, lowercase, dashes ok        |
| Family directory     | `<gateway>/<family-slug>/`, lowercase, dashes ok                     |
| Content filename     | `<stem>-v<N>.<ext>[.j2]` where `<stem>.<ext>[.j2]` matches `file`    |
| `preset_name`        | Python-style identifier, globally unique, must **not** end in `_v<N>`|
| Versioned preset     | `<preset_name>_v<N>` — generated automatically                       |
| Version-less alias   | `<preset_name>` — points at the highest-`v` file in the family       |

---

## Pre-submission checklist

Everything below should pass on your branch before opening the PR:

- [ ] `python tools/build.py --check` — manifest in sync.
- [ ] `ruff check src/ tests/ tools/` — lint clean.
- [ ] `pytest -q` — all tests pass.
- [ ] `.j2` templates render without error when fed a plausible
  listing/interface context (see the per-example CI in the sellers
  repo; local smoke is enough for a first PR).
- [ ] Package version bumped in both `pyproject.toml` and
  `src/unitysvc_data/_version.py`.
- [ ] `_manifest.json` and `MANIFEST.md` committed alongside the
  example files (build.py produces both).

---

## What CI validates

On every PR, [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
runs:

- `tools/build.py --check` — front-matter schema, `preset_name`
  uniqueness, filename conventions, manifest freshness.
- `ruff check src/ tests/ tools/` — code style.
- `pytest -q` on Python 3.11 and 3.12.
- Wheel build + a smoke check that every `.j2` file and
  `_manifest.json` ends up packaged.

On a GitHub Release,
[`.github/workflows/publish.yml`](.github/workflows/publish.yml)
builds the sdist + wheel and publishes to PyPI via OIDC.

---

## Getting help

- Design discussion: reply on
  https://github.com/unitysvc/unitysvc-sellers/issues/25 (the original
  design thread).
- Bug reports: file an issue against
  https://github.com/unitysvc/unitysvc-sellers/issues and tag with
  `unitysvc-data`.
- Questions about whether an example belongs here vs. in a seller's
  own data repo: ask in the design-discussion thread above before
  spending time on implementation — the answer affects where the work
  should live.
