+++
preset_name = "llm_code_example_chat_dashscope_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion to a DashScope-native endpoint using the requests library"
is_active = true
is_public = true
meta = { variant = "Chat (DashScope)", requirements = ["requests"], min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "chat", dialect = "dashscope", upstream = "dashscope" }
+++

# llm / dashscope-chat-requests

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

