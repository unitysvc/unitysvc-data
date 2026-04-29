+++
preset_name = "llm_code_example_transcription_requests"
category = "code_example"
mime_type = "python"
file = "code-example-transcription.py.j2"
description = "Python example: transcribe a pre-recorded audio file with an OpenAI-compatible audio transcription endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-transcription-requests — audio transcription via `requests`

Customer-facing Python example for OpenAI-compatible
`/v1/audio/transcriptions`-shaped endpoints (Whisper-class models).
Downloads an audio fixture from a public URL and uploads it as
`multipart/form-data`, then prints the transcribed text.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `AUDIO_URL` — public URL of the audio fixture to transcribe.
  Defaults to JFK's "Ask not what your country can do for you"
  inaugural quote (`tests/jfk.flac` from the openai/whisper repo,
  ~1.1 MB flac). Override with any publicly-reachable
  `mp3` / `wav` / `flac` / `m4a` URL.

## Conventions

- Pulls the audio over HTTP at script start so the example runs
  standalone — no fixture file needs to exist on disk.
- Filename used in the multipart upload is derived from the URL's
  path basename, so providers that sniff format from the filename
  see the right extension.

## Versions

### v1 — initial release

- `requests.get(AUDIO_URL)` then multipart `requests.post(...)` to
  the transcription endpoint.
- `raise_for_status()` on both calls so a download or upload
  failure exits non-zero with a clear message.
