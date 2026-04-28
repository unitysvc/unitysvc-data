+++
preset_name = "llm_code_example_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion request to an OpenAI-compatible LLM using the requests library"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-requests — chat completion via `requests`

Customer-facing Python example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the
`requests` library (no vendor SDK) so the same script works against
any provider whose endpoint is OpenAI-compatible.

The companion preset `llm_code_example_openai` shows the same call
using the `openai` Python SDK, which is what most users will reach
for if they already have it installed.

## Environment variables (all required)

- `SERVICE_BASE_URL` — OpenAI-compatible API base URL (e.g.
  `https://api.openai.com/v1` or the gateway's `/v1`-equivalent). The
  script appends `/chat/completions` to this base — same convention
  the OpenAI Python SDK uses for its `base_url` argument.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`.
- `MODEL` — interface-specific model identifier. The gateway's
  routing key and the upstream's native model id can differ for the
  same logical offering, so the caller must pass the right one for
  the access interface they're hitting.

## Versions

### v1 — initial release

- `requests.post` against `${SERVICE_BASE_URL}/chat/completions` with
  `model` + two-message `messages` array.
- `response.raise_for_status()` so non-2xx responses surface as a
  non-zero exit.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment; missing any of the three fails fast with `KeyError`.
