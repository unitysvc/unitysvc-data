+++
preset_name = "llm_request_template"
category = "request_template"
mime_type = "json"
file = "request-template.json"
description = "Minimal chat request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "chat" }
+++

# llm / request-template — minimal chat payload, per request format

The default request body the Test Request playground offers for a chat
service. One document covers one capability — this one is `chat`, as its
`applies_to` says — and from v3 it is a **list of entries**, each naming the
request format it is written in:

```json
[ { "format": "openai",    "body": { "max_tokens": 100, "messages": [ … ] } },
  { "format": "anthropic", "body": { "max_tokens": 100, "system": "…", "messages": [ … ] } } ]
```

The playground picks the document by the service's capability and then the first
entry whose `format` is the one the customer chose (unitysvc/unitysvc#2514).
Entries for formats a service doesn't accept are never read. `format` is the
gateway's name for a request format: what a service lists in `input_formats`, and
what the gateway recognises a body as by its shape (apisix-gateways
`request_meta.classify`). So every chat service ships this one document whatever
formats it accepts.

The other capabilities have their own families, `request-template-<capability>`,
each the same shape for one capability. The rules they share are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates).

## Body (v3)

| `format`           | Wire shape                                     |
|--------------------|------------------------------------------------|
| `openai`           | OpenAI Chat Completions                        |
| `anthropic`        | Anthropic Messages (`system` is top-level)     |
| `cohere`           | Cohere v2 Chat (native `/v2/chat`)             |
| `dashscope`        | DashScope native (`input.messages` + `parameters`) |
| `bedrock_converse` | Bedrock Converse (content blocks, `inferenceConfig`) |

Every entry says the same thing: system prompt "You are a helpful
assistant.", user prompt "Say hello in one sentence.", at most 100 tokens.

## What's intentionally missing

- **No `model` field.** The gateway's routing config or the listing's
  `upstream_access_config` selects the upstream model; the playground merges
  the service's routing key into the body it sends. Bedrock Converse takes the
  model id in the path instead.
- **No `stream` field.** Non-streaming responses are simpler to
  validate in tests; streaming variants belong in separate presets.
- **No `bedrock_invoke` entry.** InvokeModel's body is the model family's own
  (Anthropic-on-Bedrock, Llama, Titan, …), so there is no one body to offer. The
  code example says as much: its body is the Anthropic Messages shape, and its
  docstring tells the reader to adjust it for their model family. The playground
  falls back to a blank body.
- **No `cerebras` entry.** It is a client library, not a request format: the
  gateway has no `cerebras` format, and `llm_code_example_cerebras` declares an
  OpenAI upstream and calls `chat.completions.create` with `model` and
  `messages`, the shape of the `openai` entry.
- **One `dashscope` body, though DashScope has two chat surfaces.** The
  gateway has a single `dashscope` format, and an entry is unique per format, so
  only one body fits. This is the text-generation shape (`content` is a string,
  `result_format = "message"`), matching `llm_code_example_chat_dashscope_text_*`.
  The multimodal-generation surface (`llm_code_example_chat_dashscope_*`) takes
  `content` as a list of `{"text": …}` parts and no `result_format`, so a service
  on it is offered a body that is not its own and must edit it.

## Conventions

- `max_tokens` is kept small (≤ 100) so the request completes fast
  against any upstream regardless of per-token latency.
- A new request format gets a new entry here, in a new version.
- Where a body goes beyond what its code example sends, it is carried over
  exactly as v2 published it: the `cohere` entry's `max_tokens`, the
  `bedrock_converse` entry's `system`, and the `dashscope` entry's system message
  are not in any example, so nothing the test runner executes exercises them.

## Versions

### v3 — an entry list

- A list of `{"format", "body"}` entries instead of a dict keyed by format. The
  bodies are v2's, key for key and in the same order; only the packaging moved.
  A dict makes the format the key and leaves nothing to say about a document
  holding more than one capability; entries name their own format, and the
  playground's reader (unitysvc/unitysvc#2515) takes the first entry that
  matches, so a repeated format would be silently unreachable — which
  `tools/build.py` now refuses.
- The title, `applies_to` and preset name are unchanged, so this is the same
  document on every published service: `llm_request_template` resolves to v3 and
  re-uploading a catalog replaces the body in place.
- Needs a playground that reads entry lists (unitysvc/unitysvc#2515). That page
  reads both shapes, so data and page can ship in either order **only because
  of that** — an older page shows a list as the raw request body.

### v2 — one body per request format (superseded by v3)

- Keyed by format: `openai`, `anthropic`, `cohere`, `dashscope`,
  `bedrock_converse`. The `openai` entry is v1's body.
- `applies_to` no longer requires an OpenAI upstream, so every chat service gets
  this template whatever its dialect — which is what makes one document the
  right shape: a service accepting both OpenAI and Anthropic needs ONE default
  body, and the playground indexes it by the format the customer picked.
  `llm_request_template_anthropic` is removed rather than kept alongside; per-format
  templates would give such a service two `Default request body` documents and no
  way to say which is the default.
- Needs a playground that picks a format's entry (unitysvc/unitysvc#2508).
  An older one shows the whole map as the body.
- **Retired, not removed.** Versions are append-only, so the file stays and
  `llm_request_template_v2` still resolves for a listing that pins it; none of
  the `unitysvc-services-*` repos does. The version-less alias moved to v3, which
  is all that `llm_example_collection` ever resolves, so nothing generated serves v2.

### v1 — initial release

- Two messages (system + user), `max_tokens = 100`, no model field,
  non-streaming.
