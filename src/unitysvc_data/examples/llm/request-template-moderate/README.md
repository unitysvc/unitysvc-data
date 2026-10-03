+++
preset_name = "llm_request_template_moderate"
category = "request_template"
mime_type = "json"
file = "request-template-moderate.json"
description = "Minimal moderation request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "moderate" }
+++

# llm / request-template-moderate — minimal moderation payload, per request format

The default request body the Test Request playground offers for services that
declare the `moderate` capability (moderation). One document covers one
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
| `openai` | OpenAI Chat Completions, sent to a guard model | `llm_code_example_guard_requests` |

Each body is the request its code example sends, reduced to what is needed to send
it: the example's own values, minus the `model` the playground merges in and minus
any templated or optional parameter.

The example moderates by chatting: it sends a chat completion to a guard model and
prints the reply. It does **not** send a `/v1/moderations` request, so neither does
this. The body is chat-shaped, and its one user message is the text to classify — a
prompt-injection attempt, the same one the example sends.

## What's intentionally missing

- **No `model` field.** The playground merges the service's routing key into the
  body it sends.

## Title

`Default request body (moderation)`: the capability's registry label.

## Versions

### v1 — initial release

- One `openai` entry: a single user message for a guard model to classify.
