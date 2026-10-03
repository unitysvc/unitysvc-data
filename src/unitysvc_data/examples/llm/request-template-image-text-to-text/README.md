+++
preset_name = "llm_request_template_image_text_to_text"
category = "request_template"
mime_type = "json"
file = "request-template-image-text-to-text.json"
description = "Minimal vision (image and text) request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "image-text-to-text" }
parameters = { version_prefix = "/v1" }
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

| `format` | Wire shape | `path_suffix` | Derived from |
|----------|------------|---------------|--------------|
| `openai` | OpenAI Chat Completions, the image as an `image_url` content part | `${__version_prefix__}/chat/completions` | `llm_code_example_vision_requests` |

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

## Path

Each `path_suffix` is what that entry's code example posts to, relative to the
service's base URL. It is read off the example, and all three of its client
variants (requests, shell, JavaScript) say the same, rather than written from an
API's documentation, so it is as verified as the body is.

`${__version_prefix__}` is the parameter the OpenAI-shaped examples use for the
one segment a seller's upstream may move: `/v1` by default, `/compatibility/v1`
for Cohere's compatibility surface, `/v2` for crofai, nothing for the platform's
own facades. This family declares it with the example's default, so a listing that
sets `params.version_prefix` for its examples gets the matching path here, and one
that sets nothing gets `/v1`. A listing that differs in any other way can replace
the document by title (a sibling key beside `$llm_example_collection`).

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

**Amended in 0.2.13**: entries gained `path_suffix` (see Path above). The
playground appends nothing for an entry without one, which sends an OpenAI-shaped
body to the service's base URL and fails; bodies, formats and their order are
unchanged. The front-matter also gained `parameters = { version_prefix = "/v1" }`.
Amended in place rather than published as a v2 because, under CONTRIBUTING's "one
exception", the entries that gained a path could not be sent without it, so there
is no working behaviour to pin to, and the version-less alias carries all the
traffic: this family was released hours earlier and nothing pins it.
