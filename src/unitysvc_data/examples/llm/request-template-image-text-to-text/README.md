+++
preset_name = "llm_request_template_image_text_to_text"
category = "request_template"
mime_type = "json"
file = "request-template-image-text-to-text.json"
description = "Minimal vision (image and text) request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "image-text-to-text" }
+++

# llm / request-template-image-text-to-text — minimal vision payload, per request format

The default request body the Test Request playground offers for services that
declare the `image-text-to-text` capability (vision). One document covers one
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
| `openai` | OpenAI Chat Completions, the image as an `image_url` content part | `llm_code_example_vision_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

The request is a chat completion whose one user message has two content parts: the
prompt "Describe this image." and an `image_url` part. The image is
`../test-image.jpg` (320×240, 4,590 bytes — the one the code examples fetch),
inlined as a `data:image/jpeg;base64,…` URI. That is the example's own choice, for
the reason it gives: handing a provider a URL leaves it to fetch the bytes itself,
and some cannot reach an arbitrary host at all. It makes the body about 6 KB,
which is the cost of a request that works as written.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.
- **No `anthropic` entry.** Anthropic's image content blocks have a different shape
  and no code example sends one, so none is offered.

## Title

`Default request body (vision)`. `image-text-to-text` is unlabelled in the registry
and *carried by* the `vision` feature, which the title builder applies to every
document of the capability, so this document cannot take chat's title,
`Default request body`, on a service that declares both.

## Versions

### v1 — initial release

- One `openai` entry: a user message with a text part and an inline image part, no
  model field, non-streaming.
