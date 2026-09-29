+++
preset_name = "llm_connectivity_omni_tts_dashscope"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify an omni DashScope endpoint by synthesising a short clip"
is_active = true
is_public = false
meta = { min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "text-to-speech", dialect = "dashscope_multimodal", upstream = "dashscope" }
+++

# llm / dashscope-omni-tts-connectivity

An **omni** model reaches text-to-speech as a chat call that asks for audio
output: `parameters.modalities = ["text", "audio"]` alongside the usual
`input.messages`. It is not the `input.text` request a dedicated TTS model takes —
an omni model rejects that with `InvalidParameter: Either "prompt" or "messages"
must exist and cannot both be none`.

**Audio output is streaming-only**, which is the part worth knowing. Without
`X-DashScope-SSE: enable` the call still returns 200 and still bills
`output_tokens_details.audio_tokens`, but the reply carries only text — the audio
is silently absent. Verified both ways against the live API.

The audio arrives across frames as `content[].audio`, an **object** with
`data` (base64), `id` and `expires_at` — not a bare string. Concatenating the
`data` of every frame gives the clip.

`parameters.voice` is optional and the accepted names are model-specific
(`Ethan`, `Chelsie` and `Serena` work on the omni models; `Cherry`, which the
dedicated TTS models take, is rejected). It is left unset so the example does not
break on a model with a different roster.

Usage bills in **tokens**, with the audio counted in
`output_tokens_details.audio_tokens` — not in characters.

Assertions sit behind `{%- if not customer_display %}` so the published example
stays clean.

## Versions

### v1 — initial release

- Streams with `X-DashScope-SSE: enable`, which audio output requires.
- Collects `content[].audio.data` across frames and writes a single clip.
- No `voice`: the accepted names differ per model.
