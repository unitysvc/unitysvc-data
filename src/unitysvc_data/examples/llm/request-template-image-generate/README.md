+++
preset_name = "llm_request_template_image_generate"
category = "request_template"
mime_type = "json"
file = "request-template-image-generate.json"
description = "Minimal image generation request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "image-generate" }
+++

# llm / request-template-image-generate — minimal image generation payload, per request format

The default request body the Test Request playground offers for services that
declare the `image-generate` capability (image generation). One document covers
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
| `openai` | OpenAI Images | `llm_code_example_image_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

The example's own prompt and options. `response_format` is `b64_json`, as in the
example, which decodes the image from the response.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.

## Title

`Default request body (image)`: the capability's registry label.

## Versions

### v1 — initial release

- One `openai` entry: a prompt, `n = 1`, `size = "1024x1024"` and
  `response_format = "b64_json"`.
