+++
preset_name = "llm_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py"
description = "Python example: send a chat completion request to an OpenAI-compatible LLM"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-python — chat completion via `requests`

Customer-facing Python example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses the standard
library `requests` package (no vendor SDK) so the same script works
against any provider whose endpoint is OpenAI-compatible.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint (gateway URL or
  upstream URL in local-testing mode). The gateway sets this to its
  own `/v1/chat/completions` route; sellers may set it to the upstream
  equivalent for local testing.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`. In gateway
  mode this is the customer's UnitySVC key; in local mode it is the
  seller's upstream key.
- `MODEL` — interface-specific model identifier. The gateway's
  routing key and the upstream's native model id can differ for the
  same logical offering, so the caller must pass the right one for
  the access interface they're hitting. The script does not fall
  back to `offering.name` because that's only a hint, not a routing
  key — silently routing the request would mask config bugs.

## Conventions

- Posts a two-message payload (system + user) and prints
  `choices[0].message.content` on success.
- Surfaces non-200 responses with the upstream's status code and
  body so failures are debuggable from CI logs.
- File is plain Python (no `.j2` suffix) — there is no Jinja2
  expansion at upload time.

## Versions

### v1 — initial release

- `requests.post` against `SERVICE_BASE_URL` with `model`, `messages`.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment; missing any of the three fails fast with `KeyError`.
