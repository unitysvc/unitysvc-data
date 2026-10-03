+++
preset_name = "llm_request_template_rerank"
category = "request_template"
mime_type = "json"
file = "request-template-rerank.json"
description = "Minimal rerank request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "rerank" }
+++

# llm / request-template-rerank — minimal rerank payload, per request format

The default request body the Test Request playground offers for services that
declare the `rerank` capability. One document covers one capability, which its
`applies_to` names, and holds one entry per request format, each naming the format
it is written in. The playground picks the document by the service's capability
and then the first entry whose `format` is the one the customer chose
(unitysvc/unitysvc#2514). A service whose format has no entry is shown an explicit
empty state, never another capability's request. The rules every template shares
are in [CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates); the chat
template this follows is `../request-template/`.

## Body (v1)

| `format` | Wire shape | Derived from |
|----------|------------|--------------|
| `openai` | OpenAI-style rerank | `llm_code_example_rerank_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

One query, five candidate documents of which one answers it, and `top_n = 3`.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.

## Title

`Default request body (rerank)`: the capability's registry label.

## Versions

### v1 — initial release

- One `openai` entry: a query, five documents and `top_n = 3`.
