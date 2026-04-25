+++
preset_name = "llm_code_example_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example.js.j2"
description = "JavaScript example: send a chat completion request to an OpenAI-compatible LLM"
is_active = true
is_public = true
+++

# llm / code-example-javascript — chat completion via `fetch`

Customer-facing Node.js example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the built-in
`fetch` API (Node 18+, no `node-fetch` dependency) so it runs without
installing anything extra.

## Environment variables

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`.
- `MODEL` — optional. Defaults to the listing's `offering.name`.

## Versions

### v1 — initial release

- `fetch` POST against `SERVICE_BASE_URL` with `model` + two-message
  `messages` array.
- Top-level `await` is avoided so the script runs as a CommonJS file.
- Non-2xx responses are surfaced with status + body and exit code 1.
