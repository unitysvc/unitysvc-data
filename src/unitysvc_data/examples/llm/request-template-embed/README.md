+++
preset_name = "llm_request_template_embed"
category = "request_template"
mime_type = "json"
file = "request-template-embed.json"
description = "Minimal embeddings request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "embed" }
+++

# llm / request-template-embed — minimal embeddings payload, per request format

The default request body the Test Request playground offers for services that
declare the `embed` capability (embeddings). One document covers one capability,
which its `applies_to` names, and holds one entry per request format, each naming
the format it is written in. The playground picks the document by the service's
capability and then the first entry whose `format` is the one the customer chose
(unitysvc/unitysvc#2514). A service whose format has no entry is shown an explicit
empty state, never another capability's request. The rules every template shares
are in [CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | Derived from |
|----------|------------|--------------|
| `openai` | OpenAI Embeddings | `llm_code_example_embed_requests` |
| `cohere` | Cohere native embed, image input | `llm_code_example_embed_image_requests` |
| `dashscope` | DashScope native text embedding | `llm_code_example_embed_dashscope_requests` |
| `huggingface` | Hugging Face inference API (`/models/<model>`), sentence similarity | `llm_code_example_sentencetransformers_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

- `openai` embeds two short sentences.
- `cohere` embeds an **image**: the only Cohere embed example sends
  `input_type = "image"`, so that is the body, with the same inlined
  `../test-image.jpg` the vision template carries. A Cohere text-embedding body has
  no code example and is not offered.
- `dashscope` embeds one text.
- `huggingface` is the `/models/<model>` surface's sentence-similarity request
  (`source_sentence` scored against `sentences`), which is what the example for
  that dialect sends and what the corpus files under `embed`.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends. The Hugging Face entry takes the model in the path instead
  (`/models/<model>`).

## Title

`Default request body (embeddings)`: the capability's registry label, so it sits
beside chat's `Default request body` on a service that declares both.

## Versions

### v1 — initial release

- Four entries — `openai`, `cohere`, `dashscope`, `huggingface` — each the request
  its code example sends.
