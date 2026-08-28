+++
preset_name = "llm_connectivity_tts"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity-tts.sh.j2"
description = "Verify an OpenAI-compatible text-to-speech endpoint by synthesizing a short phrase and asserting real audio comes back"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
parameters = { version_prefix = "/v1", voice = "alloy", response_format = "wav", min_bytes = "1024" }
applies_to = { capability = "text-to-speech" }
+++

# llm / connectivity-tts — text-to-speech smoke test

Connectivity check for OpenAI-compatible **text-to-speech** services routed
through the UnitySVC LLM gateway. The standard `llm_connectivity` preset POSTs
to `/chat/completions` and is rejected by TTS-only models (they expose
`/audio/speech`, not the chat surface), which fails the whole service at review
with an upstream 4xx.

This closes the gap recorded in unitysvc/unitysvc#1781: TTS shipped code
examples but no connectivity probe, and connectivity is mandatory to activate —
so TTS services could never leave `draft` however complete their examples were.

## Asserting on audio, not JSON

Every other probe in this family greps the response body for a field —
`"choices"` for chat, `"text"` for transcription. A successful TTS response is
**audio bytes**, so there is nothing to grep. Three checks stand in for it:

1. **HTTP 2xx.**
2. **At least `min_bytes` of body.** A stub, an empty file or a short error page
   fails. 1 KiB is comfortably below a second of any real codec output and
   comfortably above an error envelope.
3. **The body does not start with `{`.** Some gateways answer 200 with a JSON
   error envelope; byte count alone would accept a long one. Only the first byte
   is inspected, so audio that happens to contain a brace later still passes.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Parameters (per-listing)

- `version_prefix` (default `/v1`) — path segment between `service_base_url`
  and `/audio/speech`. Override to e.g. `/compatibility/v1` for providers that
  expose the OpenAI-compat shape under a non-standard prefix.
- `voice` (default `alloy`) — voice id. Providers do not share a voice
  vocabulary, so a service whose upstream rejects `alloy` must set its own
  (groq's `canopylabs/orpheus-*` and parasail's `resemble-tts-en` each have
  their own list).
- `response_format` (default `wav`) — container requested from the upstream.
- `min_bytes` (default `1024`) — floor for the "this is real audio" assertion.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required.

## Route status

`/v1/audio/speech` is **unverified through the gateway** — no catalog exercises
it yet, unlike `/v1/audio/transcriptions`, which cohere ships today. This probe
is how that gets settled: running it against a real TTS service either passes,
proving the route, or produces a concrete gateway bug to file. See
unitysvc/unitysvc#1781 blocker 2.

## Versions

### v1 — initial release

- POST `/audio/speech` with model, a fixed short input, voice and
  `response_format`.
- 2xx, byte-count and not-JSON assertions as described above.
- Removes the downloaded response before exiting so repeated runs do not
  accumulate audio in the temp dir.
- Output contains `connectivity ok` — paired with the
  `output_contains = "connectivity ok"` meta so the run-tests flow can confirm
  a real round-trip.
