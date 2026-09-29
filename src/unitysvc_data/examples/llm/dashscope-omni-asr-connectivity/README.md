+++
preset_name = "llm_connectivity_omni_asr_dashscope"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify an omni DashScope endpoint by transcribing a tiny audio sample"
is_active = true
is_public = false
meta = { min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "speech-to-text", dialect = "dashscope_multimodal", upstream = "dashscope" }
+++

# llm / dashscope-omni-asr-connectivity

An **omni** model reaches speech-to-text as a chat call: an `audio` part in
`input.messages[].content`, alongside the instruction. It is not the
`input.audio` request a dedicated ASR model takes — an omni model rejects that
with `InvalidParameter: Either "prompt" or "messages" must exist and cannot both
be none`. Verified against the live API, which transcribed the sample correctly.

The reply is ordinary chat: the transcription is
`output.choices[0].message.content[0].text`. Usage bills in **tokens**, with the
audio counted in `input_tokens_details.audio_tokens` — not in characters.

Assertions check the payload rather than the status, because DashScope answers
**200 with an error envelope**. They sit behind `{%- if not customer_display %}`
so the published example stays clean.

## Versions

### v1 — initial release

- Audio by URL in a content part; the model fetches it.
- Reads the transcription from the chat reply.
