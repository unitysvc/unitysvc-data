+++
preset_name = "llm_request_template_speech_to_text"
category = "request_template"
mime_type = "json"
file = "request-template-speech-to-text.json"
description = "Minimal transcription request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "speech-to-text" }
+++

# llm / request-template-speech-to-text — minimal transcription payload, per request format

The default request body the Test Request playground offers for services that
declare the `speech-to-text` capability (transcription). One document covers one
capability, which its `applies_to` names, and holds one entry per request format,
each naming the format it is written in. The playground picks the document by the
service's capability and then the first entry whose `format` is the one the
customer chose (unitysvc/unitysvc#2514). A service whose format has no entry is
shown an explicit empty state, never another capability's request. The rules every
template shares are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | Derived from |
|----------|------------|--------------|
| `dashscope` | DashScope native, dedicated speech-recognition model | `llm_code_example_asr_dashscope_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

One user message whose content is a single `audio` part: a URL to the public JFK
sample the transcription examples all use.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.
- **No `openai` entry.** The OpenAI transcription request is `multipart/form-data` —
  a `file` upload with `model` and `language` fields
  (`llm_code_example_transcription_requests`). An entry's `body` is JSON, and
  `content_type` is not part of an entry yet (unitysvc/unitysvc#2514, step 2), so
  there is no honest entry to write: a JSON stand-in would send JSON to an endpoint
  that expects an upload. A service on the OpenAI format sees the playground's
  explicit empty state, and its code example shows the real request. Add the entry
  when multipart is supported.
- **One `dashscope` body, though DashScope has two surfaces for this.** An entry is
  unique per format and the gateway has a single `dashscope` format, so only one
  body fits. This is the dedicated speech-recognition shape
  (`dashscope_audio_task`). The omni-model shape
  (`llm_code_example_omni_asr_dashscope_requests`, `dashscope_multimodal`) adds a
  text instruction and `max_tokens`, so a service on an omni model is offered a body
  that is not its own and must edit it.

## Title

`Default request body (transcription)`: the capability's registry label.

## Versions

### v1 — initial release

- One `dashscope` entry. The OpenAI format has none, for the reason above.
