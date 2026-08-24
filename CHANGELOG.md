# Changelog

All notable changes to `unitysvc-data` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to semantic versioning — minor bumps for new
presets or new versions of existing presets, patch bumps for
non-preset fixes (build script, tests, docs), major bumps only to
remove a previously-published `_vN` preset (should be vanishingly
rare).

## [Unreleased]

## [0.1.37] — fix the translated-shell assertions the deepseek canary caught

The first live run of the 0.1.36 collection (deepseek staging, 2 services)
rejected both revisions with 5 failing documents. Root causes and fixes,
each verified by executing the fixed script against the staging gateway
before this release:

### Fixed

- **`llm_code_example_{anthropic_to_openai,openai_to_anthropic}{,_stream}_shell` v3** —
  v2 wrapped only the `local_testing` branch, so the gateway branch (the one
  staging actually runs) never printed the sentinel and every gateway run
  failed with `unexpected_output`. v3 asserts in BOTH branches, and the
  gateway branch keys the needle on the CALLER's dialect — the gateway
  replies in the style you sent, so an Anthropic-dialect caller gets
  `"content"` back even when the upstream speaks OpenAI. (v2 had keyed it
  on the upstream dialect: backwards.)

  The published v2s can never pass in gateway mode, so `[versions.v2]`
  opts them out of `output_contains` — a pinned `_v2` degrades to
  status-only instead of always-failing. Aliases resolve to v3.

- **`llm_code_example_anthropic_to_openai_stream_sdk` v2** — the v1 gateway
  branch crashed with `AttributeError: 'dict' object has no attribute
  'append'`: `client.messages.stream()` builds a full message snapshot,
  and its accumulator breaks when a translated stream deviates slightly
  from Anthropic's exact event shapes. v2 iterates RAW events
  (`messages.create(stream=True)`) and reads only the text deltas.

- The branch-aware sentinel test: every Jinja branch of an asserting
  example must be able to produce its `output_contains` (a sentinel in the
  shared tail after the final `endif` counts — bedrock-converse prints it
  there). This is the test that would have caught the v2 bug before
  release.

### Known, not fixed here

- `llm_code_example_openai_javascript` and `_streaming_openai_javascript`
  fail with `Cannot find module 'openai'`: the platform test runner
  installs Python `meta.requirements` but not JavaScript ones. Fix is in
  the runner (unitysvc backend), not this package.
- The `openai_to_anthropic` direction is corrected by symmetry but not yet
  verified on the wire — no anthropic-upstream service has adopted the
  collection yet.

## [0.1.36] — `llm_example_collection`: documents derived from capability

### Added

- **`llm_example_collection`** — a new *kind* of preset. Where `doc_preset`
  expands a sentinel into ONE document, this expands one into a whole
  `documents` block:

  ```jinja
  "documents": {{ llm_example_collection(
       capabilities = ["chat"],
       formats      = ["openai", "anthropic"],
       tools        = supports_tools) | tojson }}
  ```

  Rendering all 660 LLM services in the catalog showed `chat` alone producing
  12 distinct preset sets across 16 seller repos, of which only three
  differences encode a fact about the service — upstream dialect, which
  dialects the caller may send, and tool support. The rest was drift.

  What it derives: the examples for a (caller dialect, upstream dialect) pair —
  translated when they differ, native when they match — plus the connectivity
  preset that PROVES the capability, and the request template. A superset of
  applicable flavours, since style is not a fact about the service; `tools`
  stays a gate because `llm_code_example_fc_requests` 400s without tool
  support, and a failing code example blocks activation.

  Available as both the `$llm_example_collection` sentinel and, via
  `register_jinja_globals`, a Jinja global.

  Six keys: `capabilities`, `formats`, `upstream_dialect`, `tools`, `sleep`,
  `params`. Anything specific to one service goes in a **sibling** document —
  `expand_presets` merges sibling keys over the expanded mapping, so a listing
  can add a document the collection cannot derive, or replace one it generated,
  by title.

- **`applies_to`** front-matter on every `llm/` preset, and an `applies_to(name)`
  accessor. States when an example applies:

  ```toml
  applies_to = { capability = "chat", dialect = "anthropic",
                 upstream = "openai", feature = "streaming" }
  ```

  An absent key is no constraint, which is how a universal document
  (`llm_description`) is expressed without a special case. Selection reads
  this rather than pattern-matching preset names, so a new example family
  joins its capability the moment it is authored. Like `parameters`, it is
  build-time metadata and never reaches the document record.

- **Per-version metadata overrides** in `tools/build.py`:

  ```toml
  [versions.v1]
  meta = { output_contains = "" }
  ```

  `meta` in the front-matter is shared by every version in a directory, which
  is right for `description` and `requirements` but wrong for anything tied to
  a specific file's CONTENT. Keys here are merged over the shared meta for that
  version only; an empty value drops the key.

### Changed

- **The shell code examples now assert the response shape.** Sixteen `_v2`
  presets — `llm_code_example_{shell,anthropic_shell,embed_shell,rerank_shell,
  transcription_shell,tts_shell,guard_shell,vision_shell,image_shell,
  imagetoimage_shell,ttv_shell,sentencetransformers_shell,embed_image_shell,
  anthropic_to_openai_shell,anthropic_to_openai_stream_shell,
  openai_to_anthropic_shell,openai_to_anthropic_stream_shell}` — capture the
  response, print it, then check it:

  ```bash
  response=$(curl --fail-with-body -sS ...)
  echo "$response"
  if ! printf '%s' "$response" | grep -q '"choices"'; then
    echo 'unexpected response: no "choices" in the reply' >&2
    exit 1
  fi
  echo "example ok"
  ```

  v1 ran `curl --fail-with-body` and checked nothing else, so it asserted HTTP
  STATUS only: a 200 carrying an error object passed, and so did a 200 from a
  different capability. The needle is a contract fact per capability, not a
  provider guess — `"choices"` chat, `"content"` Anthropic message, `"data"`
  embeddings, `"results"` rerank, `"text"` transcript, `"data:"` SSE.

  Aliases resolve to v2, so consumers pick this up automatically. v1 is
  unchanged and opts out of the assertion via `[versions.v1]`.

  llm code examples asserting anything: **17 of 61, up from 1**. The remaining
  44 are python/js, which already fail structurally — they index into the
  response and raise on a wrong shape.


## [0.1.35] — generic `llm_description` v2 + `meta.variant` on code examples

### Added

- `llm_description_v2` — a rewrite of the LLM listing overview shown under
  "How to use this model". v1 described "OpenAI-compatible LLM via UnitySVC",
  but the preset is attached bare in 17 seller repos including services that
  are not OpenAI-shaped: Anthropic's native Messages API, Bedrock's Converse
  channel, Cohere's native embed and transcription surfaces. It also predated
  gateway format translation, so it never mentioned that most services accept
  both OpenAI and Anthropic input.

  v2 is platform-wide and makes no claim about which format a given service
  speaks: channels (managed / byok / byoe), where to find runnable code and
  the Test Request panel, request formats and gateway translation, and the
  `/g/` `/p/` `/a/` `/l/` `/m/` request primitives. Cross-references use the
  relative `?topic=` form, which listing documents render as topic-reader
  links.

  Service-specific facts are dropped rather than templated — base URL, model,
  price and accepted formats are already rendered from real data elsewhere on
  the listing page. That leaves nothing to interpolate, so the file stays a
  plain `.md`. This also fixes a v1 defect: its `{{ SERVICE_BASE_URL }}`,
  `{{ API_KEY }}` and `{{ MODEL }}` tokens sat in a non-`.j2` file and were
  never interpolated, so customers saw literal braces directly above code
  examples that *were* rendered with real values.

  Versions are append-only: `llm_description_v1` still resolves to the old
  text. No seller repo pins `_v1`, so the bare `llm_description` alias moves
  every consumer to v2 with no template changes.

- `meta.variant` on all 61 `llm` code-example presets — a short label naming
  the task or dialect rather than the language (`Chat`, `Anthropic-style`,
  `OpenAI-style`, `Function calling`, `Streaming`, `boto3 Converse`,
  `boto3 InvokeModel`, `Cohere SDK`, `Cerebras SDK`, `Embeddings`,
  `Image embeddings`, `Rerank`, `Transcription`, `Text to speech`,
  `Text to video`, `Vision`, `Image generation`, `Image to image`, `Guard`,
  `Sentence Transformers`).

  A service carries several examples in one language — Python has 3 on most
  listings and 5 on bedrock — and the consuming UI needs to tell siblings
  apart in a tab that already says "Python". The only text available before
  this was the document title, which is the JSON key in each seller repo's
  `listing.json.j2`: 16 distinct ones, free-form, with nothing structured
  behind them. Stating the label beats inferring it from prose.

  `variant` survives the seller-side `meta` override most templates use for
  `sleep_after_test`, because `doc_preset` merges `meta` rather than replacing
  it.

## [0.1.34] — model-family logos via `logo_preset`

### Added

- `logo_preset` resolves a model-family logo, with `list_logo_families()` /
  `resolve_family()` helpers and a `logos.toml` family table.

## [0.1.33] — bedrock converse/invoke boto3 code examples

### Added

- `llm_code_example_bedrock_converse` and `llm_code_example_bedrock_invoke` —
  boto3 examples against the native Bedrock runtime, for the converse channel
  that addresses a model by id in the URL.

## [0.1.32] — `version_prefix` for the anthropic↔openai presets

### Added

- `version_prefix` parameter support on the `anthropic_to_openai` /
  `openai_to_anthropic` presets, so a repo whose upstream is versioned
  something other than `/v1` can point the examples at it.

## [0.1.31] — code examples report the server's error message

### Fixed

- Every Python code example now raises with the response body on a non-2xx
  reply, instead of calling `raise_for_status()` and discarding it. The old form
  produced `400 Client Error: Bad Request for url: ...` — the status and nothing
  else — so a gateway or upstream rejection reached the seller test artifact with
  its actual explanation thrown away. Diagnosing a translator bug
  (unitysvc/unitysvc#1782) cost three rounds of guesswork for exactly this
  reason: the answer, `anthropic-version: header is required`, was sitting in a
  body no example printed. The JavaScript examples already did this
  (``HTTP ${status}: ${await response.text()}``); Python was the outlier.

  The check is `response.status_code >= 400` rather than `response.ok`, because
  190 of the 208 examples use `httpx`, which has no `.ok`.

- `api_code_example_shell` used `curl -fsS`, which suppresses the body on
  failure. Note that swapping in `--fail-with-body` is not enough on its own:
  that flag writes the error body to the output target, so the example's
  `-o /dev/null` discarded the very message the flag recovered. The example now
  captures the response and prints it on the failure path. A failing call went
  from `curl: (22) The requested URL returned error: 401` to that plus
  `{"error":"Missing svcpass API key. ..."}`.

### Added

- `tests/test_example_syntax.py`: renders every `*.py.j2` example in both
  `local_testing` branches and parses the result, so a bad edit fails the build
  instead of a service. Also asserts no example reintroduces bare
  `response.raise_for_status()`.

## [0.1.28] — llm: SDK-based translation code examples

### Added

- Four `llm_code_example_{anthropic_to_openai,openai_to_anthropic}[_stream]_sdk`
  presets: SDK-based counterparts to the `_requests` variants, using the OpenAI
  and Anthropic SDKs matched to each side of the translation (OpenAI SDK for the
  OpenAI side, Anthropic SDK for the Anthropic side, on whichever end
  `local_testing` selects). They declare `requirements = ["openai", "anthropic"]`
  — the tradeoff for read-clarity vs the single-`requests`-dependency variants,
  which are kept.

### Fixed

- `ruff check` now passes under ruff 0.16.2: sorted `__all__`, dropped a
  read-only `global`, explicit `subprocess.run(check=...)`, `str.removesuffix`,
  parenthesized implicit string concatenation, removed dead `# noqa: E402`, and
  marked `tools/build.py` executable. `TRY004` is ignored — the preset
  validators deliberately raise `ValueError` for bad input types (contract
  enforced by `tests/test_presets.py`).

## [0.1.27] — llm: OpenAI ⇄ Anthropic translation code examples

### Added

- Eight `llm_code_example_{anthropic_to_openai,openai_to_anthropic}_*`
  presets covering both translation directions, streaming and non-streaming,
  in Python (`requests`) and shell (`curl`). Each renders in customer-format
  against the gateway and switches to a direct native-format upstream call
  under `local_testing`. Extracted from the `unitysvc-stress` `stress-llm`
  templates so translation services can reference them as `$doc_preset`s
  instead of carrying inline example files.

## [0.1.26] — msg-to-channel: server-side channelization + local-testing auth

### Changed

- Drop the `@<channel>` suffix from every msg-to-channel connectivity and
  code-example preset; the gateway now applies the channel selector to
  `service_base_url` server-side, so the presets POST to the bare URL. Shorten
  the baked test payloads to the mock happy-path text.

### Fixed

- Restore the per-channel auth headers / native body fields in `local_testing`
  mode that `0.1.25` documented but did not actually emit — Bearer/Basic/api-key
  variants, octopush dual `api-login` + `api-key`, form-encoded prowl/pushdeer/
  synologychat, pagertree top-level `title`, simplepush `key`, smtp2go `api_key`
  — so the gateway connectivity diagnostics pass against the mock upstream.

### Docs

- Update the connectivity + code-example READMEs to describe server-side
  channelization (the preset no longer appends `@<channel>`).

## [0.1.25] — msg-to-channel upstream test fixes

### Fixed

- Add mock-compatible auth headers and native payload fields to msg-to-channel
  upstream-only local-testing examples.
- Align PagerTree, Prowl, SimplePush, SMTP2GO, Synology Chat, and Matrix
  upstream-only tests with the mock server contracts.

## [0.1.24] — maintenance release

### Changed

- Bump package version for the next `unitysvc-data` release.

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
