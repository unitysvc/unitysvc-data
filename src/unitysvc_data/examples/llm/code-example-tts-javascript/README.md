+++
preset_name = "llm_code_example_tts_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-tts.js.j2"
description = "JavaScript example: synthesize speech via OpenAI-compatible /audio/speech"
is_active = true
is_public = true
+++

# llm / code-example-tts-javascript — text-to-speech via `fetch`

Customer-facing Node.js example for OpenAI-compatible
`/audio/speech` endpoints. Saves the returned audio bytes to a
`.wav` file.

## Environment variables

Required:

- `SERVICE_BASE_URL` — TTS endpoint base URL.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — TTS model id.

Optional:

- `VOICE` — voice id (defaults to `alloy`).
- `OUTPUT_FILE` — destination path (defaults to `tts_output.wav`).

## Versions

### v1 — initial release
