+++
preset_name = "llm_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of an OpenAI-compatible LLM gateway service"
is_active = true
is_public = true
+++

# llm / description — LLM gateway service description

Markdown overview shown to customers on the listing page for any
OpenAI-compatible LLM gateway service. Frames authentication, points
to the openai SDK as the recommended client, and notes that the same
endpoint also accepts raw HTTP and the Node.js SDK.

## Template tokens — **not** Jinja2

The description contains `{{ SERVICE_BASE_URL }}`, `{{ API_KEY }}`,
and `{{ MODEL }}` — these are **literal** placeholders shown to
customers (the file is `description.md`, not `description.md.j2`,
so SDK rendering leaves them intact). Customers replace them with
their own values when copy-pasting.

## What's intentionally not covered

- Per-provider quirks (Anthropic's non-OpenAI API, provider-specific
  parameters, tier limits). Sellers who need to call those out should
  ship their own description on top of this canonical baseline.
- Function calling, vision, embeddings, audio. Those have their own
  preset code-examples that the listing can attach independently.

## Versions

### v1 — initial release

- Chat-completion quickstart via the `openai` SDK.
- Brief streaming note.
- Three placeholder tokens for the customer to fill in.
