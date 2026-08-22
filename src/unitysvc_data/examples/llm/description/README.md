+++
preset_name = "llm_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of how LLM services are consumed through the UnitySVC gateway"
is_active = true
is_public = true
+++

# llm / description — LLM gateway service description

Markdown overview shown to customers on the listing page for any LLM gateway
service, under the document key `How to use this model`. Covers what is true
of **every** LLM service on the platform — channels, request formats, and the
request primitives a service composes with — and defers everything
service-specific to the rest of the listing page.

## Deliberately generic

The document carries no service-specific facts and no template tokens. Base
URLs, model names, pricing, and the accepted format list all already appear
elsewhere on the listing page, rendered from real data; repeating them here
would only create a second copy to drift.

That is also why the file is `description.md` and **not** `description.md.j2`:
there is nothing to interpolate. (v1 did carry `{{ SERVICE_BASE_URL }}`,
`{{ API_KEY }}`, and `{{ MODEL }}` — but as a plain `.md` they were never
rendered, so customers saw the literal braces. v2 removes them rather than
converting the file to a template.)

## Topic links

Cross-references use the platform's relative topic-link form,
`[Alias](?topic=alias)`. Listing documents render through
`DocumentRenderer` → `MarkdownContent` with no sanitizer and no `a` override,
so react-markdown passes these hrefs through verbatim; the app-wide
`TopicReaderProvider` reads the `?topic=` param and opens the topic reader.

Every slug used here must exist as a file in the frontend's
`content/topics/` directory — a typo renders a link that 404s in the reader.

## What's intentionally not covered

- **Per-service facts** — accepted formats, channels offered, price, base URL.
  All are rendered from real data elsewhere on the page.
- **Runnable code.** The listing's code examples are generated per language
  with the service's real values and are the copy-paste surface; a
  hand-written snippet here would be both redundant and less accurate.
- **Client-specific recipes** (OpenWebUI, `usvc services dispatch`, coding
  agents other than Claude Code). These belong in platform topics once
  written and tested, and this document can link them when they exist.

## Versions

### v1 — initial release

- Chat-completion quickstart via the `openai` SDK.
- Brief streaming note.
- Three placeholder tokens for the customer to fill in.

### v2 — generic, format-neutral rewrite

v1 described an OpenAI-compatible service, but the preset is attached to
services that are not OpenAI-shaped — Anthropic's native Messages API,
Bedrock's Converse channel, Cohere's native embed and transcription surfaces.
It also predated the gateway's format translation, so it never mentioned that
most services accept both OpenAI and Anthropic input.

- Reframed as a platform-wide overview of consuming LLM services; no claim
  about which format a given service speaks.
- Dropped the code block and its three never-rendered placeholder tokens.
- Dropped the streaming section, which the `llm_code_example_streaming_*`
  presets cover with runnable code.
- Added channels (managed / byok / byoe), request formats, and the
  group / pool / alias / log / memoize primitives, each linking its topic.
