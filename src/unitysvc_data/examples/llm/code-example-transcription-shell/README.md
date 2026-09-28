+++
preset_name = "llm_code_example_transcription_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-transcription.sh.j2"
description = "Bash example: transcribe audio via OpenAI-compatible /audio/transcriptions using curl"
is_active = true
is_public = true
meta = { variant = "Transcription", min_expected_metrics = { duration_seconds = 0.01 } }
parameters = { version_prefix = "/v1", language = "en" }
applies_to = { capability = "speech-to-text" }
+++

# llm / code-example-transcription-shell — audio transcription via `curl`

Curl-based POST to `/audio/transcriptions` with the test audio file as multipart form data.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `AUDIO_URL` — alternate test audio URL (defaults to the Whisper JFK sample).

## Versions

### v1 — initial release

### v2 — in-script verification

- Verifies the response in the script rather than through the runner's
  `output_contains` sentinel, which was retired platform-side
  (unitysvc/unitysvc#2490) — so the check is a real status or response-shape
  assertion, not a match against a token the script printed unconditionally.
- The assertion is wrapped in `{%- if not customer_display %}` so it runs but
  stays out of the published example; the unconditional success marker is gone.
- **Amended in 0.2.2.** Earlier installs of this package ship a v2 whose
  verification lived in metadata instead.
