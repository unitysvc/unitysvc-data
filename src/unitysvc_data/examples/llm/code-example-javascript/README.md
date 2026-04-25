+++
preset_name = "llm_code_example_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example.js"
description = "JavaScript example: send a chat completion request to an OpenAI-compatible LLM"
is_active = true
is_public = true
+++

# llm / code-example-javascript — chat completion via `fetch`

Customer-facing Node.js example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the built-in
`fetch` API (Node 18+, no `node-fetch` dependency) so it runs without
installing anything extra.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

## Versions

### v1 — initial release

- `fetch` POST against `SERVICE_BASE_URL` with `model` + two-message
  `messages` array.
- A small loop checks the three required env vars before the request
  and exits 1 on any missing one.
- Non-2xx responses are surfaced with status + body and exit code 1.
- Plain JavaScript (no `.j2` suffix) — no Jinja2 expansion.
