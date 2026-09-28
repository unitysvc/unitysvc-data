+++
preset_name = "llm_connectivity_embed"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity-embed.sh.j2"
description = "Verify an OpenAI-compatible embeddings endpoint by issuing a tiny embed request"
is_active = true
is_public = false
meta = { min_expected_metrics = { input_tokens = 1 } }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "embed", dialect = "openai" }
+++

# llm / connectivity-embed — embeddings smoke test

Connectivity check for OpenAI-compatible **embedding** services routed
through the UnitySVC LLM gateway. The standard `llm_connectivity`
preset POSTs to `/chat/completions` and is rejected by embedding-only
models (they don't expose a chat surface), which causes the entire
service to fail review with an upstream 4xx.

This preset POSTs the smallest possible embed request, asserts the
gateway returned a real `data` array, and prints `connectivity ok` on
success.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream key when wired as a secret (BYOK).

## Versions

### v1 — initial release

- POST `/embeddings` with `input: "ping"` (smallest valid payload).
- `curl --fail-with-body` so 4xx / 5xx surface as non-zero exit + body in stderr.
- `grep -q '"data"'` so a 200 with an unrelated body (rare, but some
  upstream errors return 200 with an `{"error": ...}` envelope) still
  fails.
- Prints `connectivity ok` only after the embedding-shape check confirms a
  real round-trip; curl or shape failures exit non-zero.
- **Amended in 0.2.2**: verification moved into the script. The runner-side
  `output_contains` sentinel it used to rely on was retired platform-side
  (unitysvc/unitysvc#2490), so the check is now a real status or
  response-shape assertion, wrapped in `{%- if not customer_display %}` to keep
  it out of the published example. The unconditional success marker is gone.
- **Amended in 0.2.3**: `applies_to` now declares `dialect = "openai"`.
  It named only the capability, and an absent key means "no constraint" — so
  this example applied to callers writing any dialect, including ones whose
  upstream has no such endpoint. Selection metadata only: nothing this example
  does has changed, and every service that received it still does, because they
  all declare `openai`.
