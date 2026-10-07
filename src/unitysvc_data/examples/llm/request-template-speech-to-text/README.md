+++
preset_name = "llm_request_template_speech_to_text"
category = "request_template"
mime_type = "json"
file = "request-template-speech-to-text.json"
description = "Minimal transcription request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "speech-to-text" }
parameters = { version_prefix = "/v1" }
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

## Body (v2)

| `format` | Wire shape | `content_type` | `path_suffix` | Derived from |
|----------|------------|----------------|---------------|--------------|
| `dashscope` | DashScope native, dedicated speech-recognition model | JSON (absent) | none (bare base URL) | `llm_code_example_asr_dashscope_requests` |
| `openai` | OpenAI audio transcription, a file upload | `multipart/form-data` | `${__version_prefix__}/audio/transcriptions` | `llm_code_example_transcription_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

`dashscope`: one user message whose content is a single `audio` part, a URL to the
public JFK sample the transcription examples all use.

`openai`: a `multipart/form-data` upload, the audio as the `file` part with `model`
and `language` as text fields. A multipart entry's `body` holds the form's text
fields, minus the `model` the playground merges in and minus any templated
parameter; `language` is the example's `${__language__}` parameter, so the body is
empty. The playground does not send uploads (unitysvc/unitysvc#2533): it reads
`content_type` and says that the request is a file upload it does not send, rather
than the generic "no template" state it showed an OpenAI-format service before.

## Path

`openai`'s `path_suffix` is what its code example posts to, relative to the
service's base URL, read off the example (all three client variants agree).
`${__version_prefix__}` is the parameter the OpenAI-shaped examples use for the one
segment a seller's upstream may move: `/v1` by default. This family declares it with
the example's default, so a listing that sets `params.version_prefix` for its
examples gets the matching path here.

**No `path_suffix` on `dashscope`:** its example posts to the service URL itself,
so there is nothing to append and the key is omitted. The page treats a missing or
blank `path_suffix` as absent and appends nothing, which is exactly that; writing
`""` would add nothing, and `"/"` would append a trailing slash, a different
request.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.
- **No JSON stand-in for `openai`.** Until v2 there was no `openai` entry at all,
  because an entry could only be a JSON body and a JSON stand-in would send JSON to
  an endpoint that expects an upload. `content_type` now says what the request is,
  and the body holds no field the example does not send.
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

### v2 — the OpenAI request, as the upload it is

- v1's `dashscope` entry, unchanged, and an `openai` entry with
  `content_type = "multipart/form-data"`, its example's path, and an empty body
  (unitysvc/unitysvc#2533). The front-matter gained
  `parameters = { version_prefix = "/v1" }` for that path. A new version rather than
  an amendment: v1 works as published, for DashScope.

### v1 — initial release

- One `dashscope` entry. The OpenAI format had none: an entry could not say it was a
  file upload yet.
