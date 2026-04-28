+++
preset_name = "llm_code_example_openai"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion request to an OpenAI-compatible LLM using the openai SDK"
is_active = true
is_public = true
meta = { requirements = ["openai"] }
+++

# llm / code-example-openai — chat completion via the `openai` SDK

Customer-facing Python example for OpenAI-compatible chat completion
services using the official `openai` Python SDK. Pointing the SDK
at `SERVICE_BASE_URL` works against any LLM gateway preset since
they all expose an OpenAI-compatible chat-completion route.

The companion preset `llm_code_example_requests` shows the same
call using only the `requests` library, for callers who don't want
to add the `openai` dependency.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint, passed as the
  SDK's `base_url`.
- `UNITYSVC_API_KEY` — passed as the SDK's `api_key`.
- `MODEL` — interface-specific model identifier. The gateway's
  routing key and the upstream's native model id can differ for the
  same logical offering, so the caller must pass the right one for
  the access interface they're hitting.

## Versions

### v1 — initial release

- `OpenAI(base_url=..., api_key=...)` then
  `client.chat.completions.create(...)`.
- HTTP errors surface as `openai.APIStatusError` (non-zero exit
  with a clear stack trace), so no explicit status check is needed.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment; missing any of the three fails fast with `KeyError`.
