+++
preset_name = "llm_code_example_image_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-image.js.j2"
description = "JavaScript example: generate an image via OpenAI-compatible /images/generations"
is_active = true
is_public = true
meta = { variant = "Image generation", min_expected_metrics = { images_generated = 1 } }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "image-generate", dialect = "openai" }
+++

# llm / code-example-image-javascript — image generation via `fetch`

Customer-facing Node.js example for OpenAI-compatible `/images/generations` endpoints. Decodes the b64-encoded response and writes it to a PNG.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `PROMPT` — generation prompt (defaults to a known-good prompt).
- `OUTPUT_FILE` — destination path (defaults to `image.png`).

## Versions

### v1 — initial release
- **Amended in 0.2.3**: `applies_to` now declares `dialect = "openai"`.
  It named only the capability, and an absent key means "no constraint" — so
  this example applied to callers writing any dialect, including ones whose
  upstream has no such endpoint. Selection metadata only: nothing this example
  does has changed, and every service that received it still does, because they
  all declare `openai`.
