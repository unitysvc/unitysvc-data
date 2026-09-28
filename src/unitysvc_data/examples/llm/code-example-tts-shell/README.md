+++
preset_name = "llm_code_example_tts_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-tts.sh.j2"
description = "Bash example: synthesize speech via OpenAI-compatible /audio/speech using curl"
is_active = true
is_public = true
meta = { variant = "Text to speech" }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "text-to-speech", dialect = "openai" }
+++

# llm / code-example-tts-shell — text-to-speech via `curl`

Curl-based POST to `/audio/speech`; writes the returned wav audio to disk.

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
- **Amended in 0.2.3**: `applies_to` now declares `dialect = "openai"`.
  It named only the capability, and an absent key means "no constraint" — so
  this example applied to callers writing any dialect, including ones whose
  upstream has no such endpoint. Selection metadata only: nothing this example
  does has changed, and every service that received it still does, because they
  all declare `openai`.
