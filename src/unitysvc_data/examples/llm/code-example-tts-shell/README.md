+++
preset_name = "llm_code_example_tts_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-tts.sh.j2"
description = "Bash example: synthesize speech via OpenAI-compatible /audio/speech using curl"
is_active = true
is_public = true
+++

# llm / code-example-tts-shell — text-to-speech via `curl`

Curl-based POST to `/audio/speech`; writes the returned wav
audio to disk.

## Environment variables

Required:

- `UNITYSVC_API_KEY` — bearer token.

Optional:

- `VOICE` — voice id (defaults to `alloy`).
- `OUTPUT_FILE` — destination path (defaults to `tts_output.wav`).

## Versions

### v1 — initial release
