+++
preset_name = "llm_code_example_transcription_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-transcription.sh.j2"
description = "Bash example: transcribe audio via OpenAI-compatible /audio/transcriptions using curl"
is_active = true
is_public = true
+++

# llm / code-example-transcription-shell — audio transcription via `curl`

Curl-based POST to `/audio/transcriptions` with the test
audio file as multipart form data.

## Environment variables

Required:

- `UNITYSVC_API_KEY` — bearer token.

Optional:

- `AUDIO_URL` — alternate test audio URL (defaults to Whisper JFK sample).

## Versions

### v1 — initial release
