+++
preset_name = "llm_request_template_embed"
category = "request_template"
mime_type = "json"
file = "request-template-embed.json"
description = "Minimal embeddings request body for each request format"
is_active = true
is_public = true
applies_to = { capability = "embed" }
parameters = { version_prefix = "/v1" }
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

| `format` | Wire shape | `path_suffix` | Derived from |
|----------|------------|---------------|--------------|
| `openai` | OpenAI Embeddings | `${__version_prefix__}/embeddings` | `llm_code_example_embed_requests` |
| `cohere` | Cohere native embed, image input | `${__version_prefix__}/embed` | `llm_code_example_embed_image_requests` |
| `dashscope` | DashScope native text embedding | none (bare base URL) | `llm_code_example_embed_dashscope_requests` |
| `huggingface` | Hugging Face inference API (`/models/<model>`), sentence similarity | none (known limitation) | `llm_code_example_sentencetransformers_requests` |

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

**No `path_suffix` on `dashscope`:** its example posts to the service URL itself,
so there is nothing to append and the key is omitted. The page treats a missing or
blank `path_suffix` as absent and appends nothing, which is exactly that; writing
`""` would add nothing, and `"/"` would append a trailing slash, a different
request.

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
  body it sends. The Hugging Face entry takes the model in the path instead
  (`/models/<model>`).

## Title

`Default request body (embeddings)`: the capability's registry label, so it sits
beside chat's `Default request body` on a service that declares both.

## Versions

### v1 — initial release

- Four entries — `openai`, `cohere`, `dashscope`, `huggingface` — each the request
  its code example sends.

**Amended in 0.2.13**: entries gained `path_suffix` (see Path above). The
playground appends nothing for an entry without one, which sends an OpenAI-shaped
body to the service's base URL and fails; bodies, formats and their order are
unchanged. The front-matter also gained `parameters = { version_prefix = "/v1" }`.
Amended in place rather than published as a v2 because, under CONTRIBUTING's "one
exception", the entries that gained a path could not be sent without it, so there
is no working behaviour to pin to, and the version-less alias carries all the
traffic: this family was released hours earlier and nothing pins it.
