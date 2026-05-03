+++
preset_name = "llm_code_example_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion request to an OpenAI-compatible LLM using the requests library"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-requests — chat completion via `requests`

Customer-facing Python example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the
`requests` library (no vendor SDK) so the same script works against
any provider whose endpoint is OpenAI-compatible.

The companion preset `llm_code_example_openai` shows the same call
using the `openai` Python SDK, which is what most users will reach
for if they already have it installed.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `requests.post` against `${SERVICE_BASE_URL}/chat/completions` with
  `model` + two-message `messages` array.
- `response.raise_for_status()` so non-2xx responses surface as a
  non-zero exit.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment; missing any of the three fails fast with `KeyError`.
