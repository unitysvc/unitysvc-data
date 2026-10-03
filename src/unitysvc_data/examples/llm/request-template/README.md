+++
preset_name = "llm_request_template"
category = "request_template"
mime_type = "json"
file = "request-template.json"
description = "Minimal chat request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "chat" }
parameters = { version_prefix = "/v1" }
+++

# llm / request-template — minimal chat payload, per request format

The default request body the Test Request playground offers for a chat
service. One document covers one capability — this one is `chat`, as its
`applies_to` says — and from v3 it is a **list of entries**, each naming the
request format it is written in and, from v4, the path it is sent to:

```json
[ { "format": "openai", "path_suffix": "/v1/chat/completions",
    "body": { "max_tokens": 100, "messages": [ … ] } },
  { "format": "anthropic", "path_suffix": "/v1/messages",
    "body": { "max_tokens": 100, "system": "…", "messages": [ … ] } } ]
```

The playground picks the document by the service's capability and then the first
entry whose `format` is the one the customer chose (unitysvc/unitysvc#2514).
Entries for formats a service doesn't accept are never read. `format` names a
request format the way the gateway does (apisix-gateways `request_meta`, which
recognises a request as one by its path or body), and the playground compares it with the
formats the service lists in `input_formats`, so an entry is reached only by a
service that lists its format. Every chat service ships this one document whatever
formats it accepts.

## Other capabilities

Every other capability has a sibling family, `request-template-<capability>`,
holding the same shape for that one capability: `image-text-to-text`, `embed`,
`rerank`, `moderate`, `image-generate`, `video-generate`, `speech-to-text` and
`text-to-speech`. The rules they share are in
[CONTRIBUTING](../../../../../CONTRIBUTING.md#request-templates).

`image-edit` has no template. Its only code example sends `multipart/form-data`,
which an entry's JSON body cannot express until entries can carry a
`content_type` (unitysvc/unitysvc#2514), so there is no honest body to offer and
a service that declares it sees the playground's empty state. The claim is checked
against the examples (`tests/test_request_templates.py`), so it will say so when it
stops being true.

## Body (v4)

| `format`           | Wire shape                                           | `path_suffix`                            |
|--------------------|------------------------------------------------------|------------------------------------------|
| `openai`           | OpenAI Chat Completions                              | `${__version_prefix__}/chat/completions` |
| `anthropic`        | Anthropic Messages (`system` is top-level)           | `/v1/messages`                           |
| `cohere`           | Cohere v2 Chat                                       | none (SDK owns the path)                 |
| `dashscope`        | DashScope native (`input.messages` + `parameters`)   | none (bare base URL)                     |
| `bedrock_converse` | Bedrock Converse (content blocks, `inferenceConfig`) | none (known limitation)                  |

Every entry says the same thing: system prompt "You are a helpful
assistant.", user prompt "Say hello in one sentence.", at most 100 tokens.

## Path

Each `path_suffix` is what a code example for that entry's format posts to,
relative to the service's base URL. It is read off the example, and the examples
for a format agree among themselves (the OpenAI entry's requests, shell and
JavaScript variants all say `/chat/completions` after the prefix), rather than
written from an API's documentation. `tests/test_request_templates.py` re-derives
every one.

`${__version_prefix__}` is the parameter the OpenAI-shaped examples use for the
one segment a seller's upstream may move: `/v1` by default, `/compatibility/v1`
for Cohere's compatibility surface, `/v2` for crofai, nothing for the platform's
own facades. This family declares it with the example's default, so a listing that
sets `params.version_prefix` for its examples gets the matching path here, and one
that sets nothing gets `/v1`. A listing that differs in any other way can replace
the document by title (a sibling key beside `$llm_example_collection`).

`/v1/messages` carries no prefix, and that is the point rather than an omission.
The path is a function of the capability and the format the *customer* speaks, and a
translated format shows it: `llm_code_example_anthropic_to_openai_requests` calls
the OpenAI upstream at `${__version_prefix__}/chat/completions` only under
`local_testing`, while a customer calls the gateway at the literal `/v1/messages`
and the gateway translates, whatever the upstream's layout. Only a request the
gateway proxies without translating, an OpenAI-format one to an OpenAI-compatible
upstream, continues into the seller's own path, which is why that one segment is a
parameter.

Three entries have no `path_suffix`, for three different reasons:

- **`dashscope` posts to the bare service URL.** Every client variant of its example
  posts to the service URL itself, so there is nothing to append and the key is
  omitted. The page treats a missing or blank `path_suffix` as absent and appends
  nothing, which is exactly that; writing `""` would add nothing, and `"/"` would
  append a trailing slash, a different request.
- **`cohere`'s example hands the base URL to the SDK**, which appends the path
  itself, so no example states it, and the playground's own format registry already
  carries the native Cohere chat path. The entry needs no key of its own.
- **Known limitation: `bedrock_converse`.** Its path carries the model id, and the
  right value varies by service inside this one entry: a native-runtime interface
  already carries `/model/<modelId>` in its URL, so a literal `/converse` would do,
  while a shared provider path builds `<service URL>-runtime/model/<modelId>/converse`
  (the example has both branches). A `path_suffix` is one string per capability and
  format, so it cannot say "it depends on the service", and the page merges `model`
  into the body rather than substituting inside the path. That is a gap in the
  contract (unitysvc/unitysvc#2514, noted on #2516), not an oversight and not
  something a template can work around, so no substitution syntax is invented here.
  The Hugging Face entries in the `embed` and `video-generate` families are the same
  limitation.

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

### v4 — a path for each entry

- Entries gained `path_suffix`: `openai` and `anthropic` have one, read off their
  examples; `cohere`, `dashscope` and `bedrock_converse` do not, each for the reason
  under Path. The bodies, the formats and their order are v3's, and a test pins that.
- **A new version, not an amendment of v3.** CONTRIBUTING's "one exception" needs
  the old behaviour to be gone, and chat's is not: the playground falls back to the
  format's own default path for a chat request, so a template without paths works on
  every service whose OpenAI surface is at `/v1`. v3 stays exactly as published, with
  no paths, for a listing that pins it. (The eight sibling families were amended in
  place instead: a template for a non-chat capability without a path cannot be sent,
  so their v1 had nothing working to pin to.)
- The front-matter gained `parameters = { version_prefix = "/v1" }`. It is shared by
  every version of the family, but v1 to v3 contain no placeholder, so their content
  is byte-identical; only the record's `file_path` now points at a per-process copy,
  as for any preset that declares parameters.
- `llm_request_template` resolves to v4. Needs nothing of the page: it ignores keys
  it does not read, so data and page can ship in either order, and a page that reads
  `path_suffix` falls back to today's behaviour for an entry that has none.

### v3 — an entry list (superseded by v4)

- A list of `{"format", "body"}` entries instead of a dict keyed by format. The
  bodies are v2's, key for key and in the same order; only the packaging moved.
  A dict makes the format the key and leaves nothing to say about a document
  holding more than one capability; entries name their own format, and the
  playground's reader (unitysvc/unitysvc#2515) takes the first entry that
  matches, so a repeated format would be silently unreachable — which
  `tools/build.py` now refuses.
- The title, `applies_to` and preset name are unchanged, so this is the same
  document on every published service: `llm_request_template` resolved to v3 in
  0.2.12 (it resolves to v4 from 0.2.13) and re-uploading a catalog replaces the body
  in place.
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
  the `unitysvc-services-*` repos does. The version-less alias has moved on (v3,
  now v4), which is all that `llm_example_collection` ever resolves, so nothing
  generated serves v2.

### v1 — initial release

- Two messages (system + user), `max_tokens = 100`, no model field,
  non-streaming.
