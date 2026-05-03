+++
preset_name = "llm_connectivity_transcription"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity-transcription.sh.j2"
description = "Verify an OpenAI-compatible audio-transcription endpoint by sending a tiny known audio file"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
parameters = { version_prefix = "/v1", language = "en" }
+++

# llm / connectivity-transcription — audio transcription smoke test

Connectivity check for OpenAI-compatible **transcription** services
routed through the UnitySVC LLM gateway.  The standard
`llm_connectivity` preset POSTs to `/chat/completions` and is rejected
by transcription-only models (they expose `/audio/transcriptions`,
not the chat surface), which causes the entire service to fail review
with an upstream 4xx.

Downloads a tiny JFK audio sample to the OS temp dir, POSTs it to
`/audio/transcriptions`, asserts the response contains a `text` field,
and prints `connectivity ok` on success.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Parameters (per-listing)

- `version_prefix` (default `/v1`) — path segment between
  `service_base_url` and `/audio/transcriptions`.  Override to e.g.
  `/compatibility/v1` for providers that expose the OpenAI-compat shape
  under a non-standard prefix (Cohere).

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required.

## Versions

### v1 — initial release

- Downloads JFK FLAC sample into `${TMPDIR:-/tmp}` if not already cached.
- POST `/audio/transcriptions` with the audio + model.
- `curl --fail-with-body` so 4xx / 5xx surface as non-zero exit.
- `grep -q '"text"'` so a 200 with an unrelated body still fails.
- Output contains `connectivity ok` — paired with the
  `output_contains = "connectivity ok"` meta so the run-tests flow can
  confirm a real round-trip.
