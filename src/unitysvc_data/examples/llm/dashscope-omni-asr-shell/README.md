+++
preset_name = "llm_code_example_omni_asr_dashscope_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: transcribe audio with an omni model on a DashScope-native endpoint via curl"
is_active = true
is_public = true
meta = { variant = "Transcription (DashScope omni)", min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "speech-to-text", dialect = "dashscope_multimodal", upstream = "dashscope" }
+++

# llm / dashscope-omni-asr-shell

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
