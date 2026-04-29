+++
preset_name = "llm_code_example_tts_requests"
category = "code_example"
mime_type = "python"
file = "code-example-tts.py.j2"
description = "Python example: synthesize speech from text using an OpenAI-compatible audio/speech endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-tts-requests — text-to-speech via `requests`

Customer-facing Python example for OpenAI-compatible
`/v1/audio/speech`-shaped endpoints. Sends a short prompt, writes
the returned audio to a `.wav` file.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `VOICE` — voice id. Defaults to `alloy` (a name shared by several
  OpenAI-compatible upstreams). Override per provider.
- `OUTPUT_FILE` — destination path. Defaults to `tts_output.wav`.

## Conventions

- Requests `wav` so the resulting file plays without a transcoder on
  any platform.
- Writes the raw response body (binary audio) to disk; non-2xx
  responses still print the error JSON before exiting.

## Versions

### v1 — initial release

- POST `model` + `input` + `voice` + `response_format=wav`.
- No vendor SDK; `requests` only.
- Required env vars fail fast with `KeyError` if missing.
