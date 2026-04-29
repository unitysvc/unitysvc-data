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

Curl-based POST to `/audio/transcriptions` with the test audio file as multipart form data.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `AUDIO_URL` — alternate test audio URL (defaults to the Whisper JFK sample).

## Versions

### v1 — initial release
