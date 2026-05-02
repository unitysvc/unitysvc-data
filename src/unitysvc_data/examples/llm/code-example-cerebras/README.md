+++
preset_name = "llm_code_example_cerebras"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion request via the cerebras-cloud-sdk"
is_active = true
is_public = true
meta = { requirements = ["cerebras-cloud-sdk"] }
+++

# llm / code-example-cerebras — chat completion via the `cerebras-cloud-sdk`

Customer-facing Python example for Cerebras-hosted LLM services. The
underlying `POST /v1/chat/completions` endpoint is OpenAI-compatible —
this preset just shows the call using the `cerebras-cloud-sdk` so
users who already have that SDK installed can copy-paste idiomatic
code without juggling base URLs and headers manually.

If you don't have `cerebras-cloud-sdk` installed, `llm_code_example_openai`
hits the same endpoint with the OpenAI SDK; `llm_code_example_requests`
uses bare `requests`. All three render the same shape.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway
  access, or an upstream key when the seller / customer wires it as a
  secret (BYOK). The Cerebras SDK accepts it via the `api_key` kwarg
  and adds the `Authorization: Bearer …` header itself.

## Versions

### v1 — initial release

- `Cerebras(base_url=..., api_key=...)` then `client.chat.completions.create(...)`.
- HTTP errors surface as `cerebras.cloud.sdk.APIStatusError` (non-zero
  exit), so no explicit status check is needed.
- Reads `UNITYSVC_API_KEY` from the environment; missing it fails fast
  with `KeyError`.
