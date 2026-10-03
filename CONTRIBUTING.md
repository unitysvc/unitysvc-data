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

| Field        | Default  | Purpose                                    |
|--------------|----------|--------------------------------------------|
| `is_active`  | `true`   | Document is active on the listing          |
| `is_public`  | `false`  | Document is customer-visible               |
| `meta`       | `{}`     | Free-form metadata (e.g. `requirements`)   |
| `parameters` | `{}`     | Per-listing string params (see below)      |

### Parameters — per-listing customisation of the example body

Use `parameters` when a single example file needs to differ slightly
between listings — for example a path fragment, a version suffix, or
any other constant that varies per provider. Without this, you end up
duplicating an entire preset (one per provider) just to change a few
characters; with it, every provider points at the same preset and
overrides only what differs.

**1. Declare the parameter in front-matter**, with a string default.
The default is a real value — pick one that makes the preset render
correctly without any override:

```toml
parameters = { version_prefix = "/v1" }
```

**2. Reference it in the example body** as `${__name__}` (note the
*double* underscores around the name — single-underscore `${VAR}`
references are left alone so you can still write shell variables in
`.sh.j2` examples without collision):

```python
client = OpenAI(
    base_url="{{ service_base_url }}${__version_prefix__}",
    api_key=os.environ["UNITYSVC_API_KEY"],
)
```

The placeholder *is* the parameter — don't repeat what's already
inside it. The default `/v1` already includes the leading slash and
version segment, so writing `${__version_prefix__}/v1` in the body
would produce `/v1/v1` on the default render.

When fetched without an override, `${__version_prefix__}` becomes
`/v1`, so the URL renders as `{{ service_base_url }}/v1` — identical
to a preset that hard-codes the path. Existing presets without a
`parameters` block render identically to before.

**3. Override per-listing** in `listing.json`. The flat dispatch form
already accepts metadata overrides like `description` and `is_public`
alongside the preset `name`; parameter overrides ride in the same
shape — the resolver auto-discriminates by checking each key against
the preset's declared parameters:

```json
{
  "Python code example": {
    "$doc_preset": {
      "name": "llm_code_example_openai",
      "version_prefix": "/compatibility/v1"
    }
  }
}
```

Now the URL becomes `{{ service_base_url }}/compatibility/v1`,
matching Cohere's OpenAI-compatibility layer at
`https://api.cohere.ai/compatibility/v1` — without a Cohere-specific
preset.

Mix overrides and parameters freely; the resolver routes each by name:

```json
{
  "Python code example": {
    "$doc_preset": {
      "name": "llm_code_example_openai",
      "description": "Cohere-compat chat",
      "version_prefix": "/compatibility/v1"
    }
  }
}
```

**Programmatic Python call sites** use the same pattern as kwargs:

```python
from unitysvc_data import doc_preset, file_preset

# Default: identical to a preset with /v1 hard-coded
file_preset("llm_code_example_openai")

# Override
file_preset("llm_code_example_openai", version_prefix="/compatibility/v1")

# doc_preset returns a record where file_path already points at the
# substituted body — consumers reading file_path get the rendered
# output without needing to know parameters exist.
record = doc_preset(
    "llm_code_example_openai",
    description="Cohere-compat chat",
    version_prefix="/compatibility/v1",
)
# record["description"] == "Cohere-compat chat"
# record["file_path"] → tmp file with substituted body
# Path(record["file_path"]).read_text() returns the substituted content
```

When parameters are supplied, `doc_preset` writes the substituted body
to a per-process tmp file and points `file_path` at that — so the
seller SDK, the upload pipeline, and the platform's Celery worker
all read the rendered output transparently. Identical
`(preset, params)` pairs reuse the same tmp file via a content-addressed
filename; the tmp directory is cleaned up on interpreter exit.

Parameter names and metadata-override names cannot collide —
`tools/build.py` enforces that no parameter is declared with a name
matching `description` / `is_public` / `is_active` / `meta`. So the
auto-discrimination is unambiguous.

**Validation**:

- Parameter defaults must be strings — `version_prefix = "/v1"` is
  fine, `max_tokens = 100` is rejected with "must be a string". If you
  need a numeric value in the body, write the literal in the body and
  only parameterise the parts that genuinely vary by string.
- Parameter names cannot collide with metadata override keys
  (`description`, `is_public`, `is_active`, `meta`) — the flat-form
  resolver discriminates by name, so a collision would be ambiguous.
- `file_preset(...)` rejects unknown parameter names from the **caller
  side** (typo protection — passing `version_prefix` to a preset that
  declared `path_prefix` raises). It does **not** reject undeclared
  `${__name__}` references in the **body** — those pass through
  verbatim at substitution time. Authors may have literal placeholders
  for documentation, future parameters, or any other reason; the
  resolver only substitutes what's declared and leaves the rest alone.

**When NOT to use parameters**:

- The varying piece is more than a small text fragment. If two
  providers diverge by a whole code block (e.g. different SDK shapes),
  ship a provider-flavoured preset instead — see
  `llm_code_example_anthropic` / `llm_code_example_cerebras` /
  `llm_code_example_cohere` as examples.
- The variant only matters for one provider on a one-off basis. Inline
  the value in a separate, narrowly-scoped preset rather than
  parameterising a shared preset that 20+ providers consume.

**Backwards compatibility**: presets without a `parameters` block (the
overwhelming majority today) read no field, get an empty dict in the
manifest, take the no-substitution fast path in `file_preset`, and
behave exactly as before.

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
presets are additive, a **minor** bump (e.g. `0.2.0 → 0.2.2`) is right.

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
package upgrades. If you need to change v1, the answer is almost
always "publish v2."

### The one exception, and how to tell whether you have it

0.2.2 amended ~600 existing examples in place instead of publishing new
versions, because a new version would have protected nobody. Two facts have to
hold together before you may do the same:

1. **The behaviour being preserved no longer exists.** `output_contains` was
   retired platform-side (unitysvc/unitysvc#2490): ingest strips the key, and a
   v1 that still declared it verified nothing. There was no working old
   behaviour left to pin to — only a check that read as if it worked.
2. **The version-less alias carries essentially all the traffic.** Publishing
   a v2 repoints the alias, so every caller using `llm_connectivity` rather
   than `llm_connectivity_v1` moves on release anyway. Before 0.2.2 exactly one
   preset was version-pinned in real seller data across every repo we publish;
   the rest tracked the alias. A version bump would have imposed the same change
   on the same callers, while leaving ~600 dead files nothing resolves to.

Note also that `meta` in the front-matter is shared by every version in the
directory, so removing a key there changes v1 too. Bumping the version does not
insulate old versions from a metadata change unless you also add a
`[versions.vN]` override — which is why the versioned form of this migration
would have left v1 with neither its metadata check nor an in-script one.

If either fact fails — the old behaviour still works, or a caller pins the
version you want to edit — publish a new version. Amending in place is a
one-time answer to a retired mechanism, not a shortcut around versioning. When
you do amend, say so in the family's README under the version you changed
(`**Amended in <release>**: …`), so a reader whose installed package predates it
can tell why the behaviour differs.

---

## Audience-scoped code: `{% if not customer_display %}`

An example serves two audiences. The seller test runner and the health sweep
**execute** it; the customer-facing projection renders it again with
`customer_display` set and shows the result on the marketplace. Wrapping a
block hides it from the second without hiding it from the first:

```jinja
{%- if not customer_display %}
n = 0
{%- endif %}
for chunk in stream:
{%- if not customer_display %}
    n += 1
{%- endif %}
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
{%- if not customer_display %}
if not n:
    raise SystemExit("unexpected response: the stream yielded no chunks")
{%- endif %}
```

Use it for anything that only makes sense while something is *verifying* the
example: assertions about the reply, `echo "example ok"`-style success markers,
`grep -q` gates that turn a response into an exit code, and the counters or
captures those need.

Do **not** use it to hide two things. **Explanatory comments** — those are the
reason an example is worth publishing; if a comment explains a check you are
wrapping, move the comment inside the wrap with it rather than leaving it
describing code the reader cannot see. And **error handling** — `if
(!response.ok) throw new Error(...)`, `main().catch(e => { …; process.exit(1) })`,
`response.raise_for_status()`, a shell `exit 1` on a failed call. Those are the
idiomatic shapes of the language and a customer needs to see them; hiding them
publishes an example that silently swallows failures, which is worse than
publishing an assertion. The checker deliberately does not flag them.

### The rules, all enforced by `tests/test_customer_display.py`

**The condition is always `not customer_display`.** Never `{% if customer_display %}`.
Every document renderer uses a lenient Jinja environment, so an absent flag is
falsy, and only the `not` form degrades to "execute the checks" on a renderer
that does not supply it yet. The inverted form silently strips assertions
instead — the failure this whole mechanism exists to prevent.

**No `{% else %}` and no `{% elif %}`.** An else-arm is shown to customers and
never executed, so nothing tests it and it rots invisibly. If the two
audiences need different code, the customer-facing half is untested by
construction — which is not a thing this flag may be used to build.

**Removal only.** The `customer_display` render must be an ordered line
subsequence of the default render: same lines, same order, duplicates
preserved. Hidden code may observe and assert; removing it must not change the
request or any visible behaviour.

**Tags sit on their own line and open with `{%-`.** The trim is not cosmetic:
a plain `{% if %}` leaves its own newline in the output, so wrapping an
existing example inserts a blank line and *changes what the runner executes*.
With `{%-` the executed render is byte-identical to the unwrapped original, so
migrating an example is invisible to everything that renders it — which is what
makes wrapping the existing corpus a safe, mechanical change rather than a
behavioural one.

### The scaffolding baseline

`tests/customer_display_baseline.txt` lists examples whose execution-only code
is not wrapped yet. It is a ratchet: a file with scaffolding that is *absent*
from the list fails the build, and so does a listed file that no longer has
any — so the list cannot go stale, and may only shrink.

**As of 0.2.2 it is empty**, which makes the check a hard rule: an example with
unwrapped verification fails the build, full stop. Keep it that way. If you
genuinely must land one unwrapped, add its path and treat the line as a promise
to come back.

Run the checker directly while authoring:

```bash
python tools/customer_display.py                     # the whole corpus
python tools/customer_display.py path/to/example.j2  # one file
```

---

## Request templates

A `request_template` is what the Test Request playground starts a request from.
It picks a document by the capability its `applies_to` names, then the first
entry in that document that names the format the customer chose
([unitysvc#2514](https://github.com/unitysvc/unitysvc/issues/2514)). That fixes
the shape:

- **One document per capability.** `applies_to = { capability = "<capability>" }`
  and nothing else: the document bundles every format, so it has no `dialect`,
  and the playground matches on capability alone. Selection needs no code --
  `llm_example_collection` picks it the way it picks every document
  (`presets._applies`), so a service gets the template for each capability it
  declares and no other. Give each capability a directory of its own
  (`request-template-<capability>/`): a `request-template-<capability>-v1.json`
  filed inside another family is a variant, which inherits that README's
  `applies_to` -- the wrong capability, and a title that replaces the other's.
- **A list of entries, each naming its format.**

  ```json
  [ { "format": "openai",    "body": { "...": "..." } },
    { "format": "anthropic", "body": { "...": "..." } } ]
  ```

  The reader takes the first entry that names the format and ignores keys it does
  not know, which is how `path_suffix` and `content_type` can arrive later.
  `tools/build.py` fails on what the reader could never reach: a repeated
  `format`, a missing or unregistered one, a missing `body`, and a latest version
  that is not a list. Older versions keep the shape they were published in.
- **`format` is a request format, not a client.** Use the gateway's name for it
  (`openai`, `anthropic`, `cohere`, `dashscope`, `bedrock_converse`, ...), which
  must be registered in `classifiers.DIALECTS`. A client library for a format
  already listed is not a format of its own (`cerebras` is one for `openai`),
  and the three DashScope tokens (`dashscope_text`, `dashscope_multimodal`,
  `dashscope_audio_task`) are surfaces of the one `dashscope` format, so a
  document holds one DashScope body per capability and has to pick. The
  playground compares `format` with the formats a service lists in
  `input_formats`, so an entry is reached only by a service that lists its
  format; one no catalog declares yet is dead data until one does.
- **Derive each body from the code example for that capability and format**,
  reduced to the request it sends -- no `model` (the playground merges the routing
  key in) and no templated parameters. Do not write one from memory: the examples
  are what `run-tests` sends to real upstreams, and nothing else here is. If the
  request is not a JSON body (`multipart/form-data`, or one that only works with a
  header the entry cannot carry), there is no honest entry yet. No document is
  better than a wrong one, and the playground shows an explicit empty state.
- **Do not choose a title.** It is derived, and it is the document's key: the
  backend upserts on `(entity_id, context_type, title)`, so two templates for one
  service with the same title would silently replace each other. Chat's is
  `Default request body` and must never change; every other capability adds its
  label (`Default request body (embeddings)`), and image-text-to-text reads
  `(vision)`, the feature the registry says carries it. None of these is yours to set.
- **A new shape is a new version.** The alias moves to it and the older versions
  stay, exactly as for any other preset. Do not amend a published version.

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
