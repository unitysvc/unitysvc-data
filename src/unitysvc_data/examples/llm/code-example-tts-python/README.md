+++
preset_name = "llm_code_example_tts_python"
category = "code_example"
mime_type = "python"
file = "code-example-tts.py"
description = "Python example: synthesize speech from text using an OpenAI-compatible audio/speech endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-tts-python — text-to-speech

Customer-facing Python example for OpenAI-compatible
`/v1/audio/speech`-shaped endpoints. Sends a short prompt, writes
the returned audio to a `.wav` file.

## Environment variables

Required:

- `SERVICE_BASE_URL` — TTS endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

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
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
