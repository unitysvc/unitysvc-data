+++
preset_name = "llm_code_example_transcription_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-transcription.js.j2"
description = "JavaScript example: transcribe audio via OpenAI-compatible /audio/transcriptions"
is_active = true
is_public = true
parameters = { version_prefix = "/v1", language = "en" }
+++

# llm / code-example-transcription-javascript — audio transcription via `fetch`

Customer-facing Node.js example for OpenAI-compatible `/audio/transcriptions` endpoints. Downloads a small sample audio file (Whisper's JFK clip) and posts it as multipart form data.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `AUDIO_URL` — alternate test audio URL.

## Versions

### v1 — - initial release
- Native `fetch` / `FormData` / `Blob` (Node 18+, no extra deps).
- Falls back to a public Whisper sample so the example runs out-of-the-box.
