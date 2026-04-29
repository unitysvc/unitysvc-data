+++
preset_name = "llm_code_example_transcription_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-transcription.js.j2"
description = "JavaScript example: transcribe audio via OpenAI-compatible /audio/transcriptions"
is_active = true
is_public = true
+++

# llm / code-example-transcription-javascript — audio transcription via `fetch`

Customer-facing Node.js example for OpenAI-compatible
`/audio/transcriptions` endpoints. Downloads a small sample audio
file (Whisper's JFK clip) and posts it as multipart form data.

## Environment variables

Required:

- `SERVICE_BASE_URL` — transcription endpoint base URL.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model id (caller must provide).

Optional:

- `AUDIO_URL` — alternate test audio URL.

## Conventions

- Uses native `fetch`, `FormData`, `Blob` — Node 18+, no extra deps.
- Falls back to a public Whisper sample if `AUDIO_URL` is unset, so
  the example is runnable out-of-the-box.

## Versions

### v1 — initial release
