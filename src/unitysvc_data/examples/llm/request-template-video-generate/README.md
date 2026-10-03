+++
preset_name = "llm_request_template_video_generate"
category = "request_template"
mime_type = "json"
file = "request-template-video-generate.json"
description = "Minimal video generation request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "video-generate" }
+++

# llm / request-template-video-generate — minimal video generation payload, per request format

The default request body the Test Request playground offers for services that
declare the `video-generate` capability (video generation). One document covers
one capability, which its `applies_to` names, and holds one entry per request
format, each naming the format it is written in. The playground picks the document
by the service's capability and then the first entry whose `format` is the one the
customer chose (unitysvc/unitysvc#2514). A service whose format has no entry is
shown an explicit empty state, never another capability's request. The rules every
template shares are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | `path_suffix` | Derived from |
|----------|------------|---------------|--------------|
| `huggingface` | Hugging Face inference API (`/models/<model>`), text to video | none (known limitation) | `llm_code_example_ttv_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

A single `inputs` prompt. The response is the video itself, as bytes.

## Path

**Known limitation: no `path_suffix` on `huggingface`.** The path carries the
service's own model name (`/models/<model>`), so the right value differs by
service, and a `path_suffix` is one string per capability and format: it cannot
say "it depends on the service". The page merges `model` into the body and does
not substitute inside `path_suffix`. That is a gap in the contract
(unitysvc/unitysvc#2514, noted on #2516), not an oversight and not something a
template can work around, so no substitution syntax is invented here. The
playground appends nothing, as it did before the key existed.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends. Hugging Face takes the model in the path instead
  (`/models/<model>`).

## Title

`Default request body (video)`: the capability's registry label.

## Versions

### v1 — initial release

- One `huggingface` entry: a text prompt under `inputs`.
