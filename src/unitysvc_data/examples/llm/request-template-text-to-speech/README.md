+++
preset_name = "llm_request_template_text_to_speech"
category = "request_template"
mime_type = "json"
file = "request-template-text-to-speech.json"
description = "Minimal speech synthesis request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "text-to-speech" }
+++

# llm / request-template-text-to-speech — minimal speech synthesis payload, per request format

The default request body the Test Request playground offers for services that
declare the `text-to-speech` capability (speech synthesis). One document covers
one capability, which its `applies_to` names, and holds one entry per request
format, each naming the format it is written in. The playground picks the document
by the service's capability and then the first entry whose `format` is the one the
customer chose (unitysvc/unitysvc#2514). A service whose format has no entry is
shown an explicit empty state, never another capability's request. The rules every
template shares are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | Derived from |
|----------|------------|--------------|
| `openai` | OpenAI Speech | `llm_code_example_tts_requests` |
| `dashscope` | DashScope native, dedicated speech-synthesis model | `llm_code_example_tts_dashscope_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

- `openai` is the example's text, `voice = "alloy"` and `response_format = "wav"`;
  the reply is the audio itself.
- `dashscope` is the dedicated-model shape: `input.text` and a voice under
  `parameters`.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.
- **One `dashscope` body, though DashScope has two surfaces for this.** An entry is
  unique per format, so only one body fits. This is the dedicated shape
  (`dashscope_audio_task`). The omni-model shape
  (`llm_code_example_omni_tts_dashscope_requests`, `dashscope_multimodal`) is left
  out for a second reason as well: audio output there is streaming-only and needs
  the `X-DashScope-SSE: enable` header. Without it the call still returns 200 and
  still bills audio tokens, but the reply carries only text. An entry has no place
  for a header, so offering that body would invite exactly that.

## Title

`Default request body (speech)`: the capability's registry label.

## Versions

### v1 — initial release

- Two entries, `openai` and `dashscope`, each the request its code example sends.
