+++
preset_name = "llm_code_example_asr_dashscope_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: transcribe audio on a DashScope-native endpoint via curl"
is_active = true
is_public = true
meta = { variant = "Speech to text (DashScope)", min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "speech-to-text", dialect = "dashscope", upstream = "dashscope" }
+++

# llm / dashscope-asr-shell

DashScope is QwenCloud's native API, and for these capabilities it is the
**only** one: `/compatible-mode/v1/audio/speech`, `/images/generations` and
`/audio/transcriptions` all answer **404**, while `/compatible-mode/v1/models`
happily lists the TTS, ASR and image models. The models are served; the
OpenAI-shaped routes to them are not.

Chat is the exception — it *is* served on the compatibility layer — and has a
DashScope example anyway, so a seller can offer the native surface without
switching dialects between capabilities.

Every request and response shape below was captured from the live API, not read
from documentation.

## The endpoint

`aigc/multimodal-generation/generation` serves **chat, text-to-speech and
speech-to-text**; only the `input` shape differs. Embeddings live at
`embeddings/text-embedding/text-embedding`. The service's own `base_url` carries
the full native path, so the example posts to the service URL with no suffix.

## Versions

### v1 — initial release

