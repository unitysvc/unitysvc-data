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

Customer-facing Node.js example for OpenAI-compatible `/audio/speech` endpoints. Saves the returned audio bytes to a `.wav` file.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `VOICE` — voice id (defaults to `alloy`).
- `OUTPUT_FILE` — destination path (defaults to `tts_output.wav`).

## Versions

### v1 — initial release
