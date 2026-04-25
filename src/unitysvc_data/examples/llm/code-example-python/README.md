+++
preset_name = "llm_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
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

## Environment variables

- `SERVICE_BASE_URL` — chat-completion endpoint (gateway URL or
  upstream URL in local-testing mode). The gateway sets this to its
  own `/v1/chat/completions` route; sellers may set it to the upstream
  equivalent for local testing.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`. In gateway
  mode this is the customer's UnitySVC key; in local mode it is the
  seller's upstream key.
- `MODEL` — optional override. Defaults to the listing's
  `offering.name`, rendered at upload time.

## Conventions

- Posts a two-message payload (system + user) and prints
  `choices[0].message.content` on success.
- Surfaces non-200 responses with the upstream's status code and
  body so failures are debuggable from CI logs.

## Versions

### v1 — initial release

- `requests.post` against `SERVICE_BASE_URL` with `model`, `messages`.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment.
- Renders `{{ offering.name }}` as the default model.
