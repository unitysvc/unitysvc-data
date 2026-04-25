+++
preset_name = "llm_code_example_transcription_python"
category = "code_example"
mime_type = "python"
file = "code-example-transcription.py.j2"
description = "Python example: transcribe a pre-recorded audio file with an OpenAI-compatible audio transcription endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-transcription-python — audio transcription

Customer-facing Python example for OpenAI-compatible
`/v1/audio/transcriptions`-shaped endpoints (Whisper-class models).
Uploads a local audio file as `multipart/form-data` and prints the
transcribed text.

## Environment variables

- `SERVICE_BASE_URL` — transcription endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.
- `AUDIO_FILE` — path to a local audio file. Defaults to `audio.mp3`
  in the working directory; sellers running this in CI usually drop a
  short test clip alongside the script.

## Conventions

- Sends `multipart/form-data` with two fields: `file` (binary) and
  `model`.
- Reads the response's `text` field (OpenAI-compatible response
  shape) and falls back to the raw body if the field is missing so
  divergent providers still surface useful debugging output.

## Versions

### v1 — initial release

- Multipart upload via `requests`, no SDK dependency.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL`, `AUDIO_FILE`
  from env.
