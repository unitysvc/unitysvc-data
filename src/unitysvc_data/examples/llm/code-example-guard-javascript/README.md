+++
preset_name = "llm_code_example_guard_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-guard.js.j2"
description = "JavaScript example: send an unsafe prompt to a guard/safety model via /chat/completions"
is_active = true
is_public = true
+++

# llm / code-example-guard-javascript — safety guard probe via `fetch`

Customer-facing Node.js example for guard/safety classifier
models served behind an OpenAI-compatible `/chat/completions`
endpoint. Sends a known-unsafe prompt so the response demonstrates
the classifier's verdict.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat completions endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — guard model id.

## Versions

### v1 — initial release
