+++
preset_name = "llm_code_example_image_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-image.js.j2"
description = "JavaScript example: generate an image via OpenAI-compatible /images/generations"
is_active = true
is_public = true
+++

# llm / code-example-image-javascript — image generation via `fetch`

Customer-facing Node.js example for OpenAI-compatible
`/images/generations` endpoints. Decodes the b64-encoded response
and writes it to a PNG.

## Environment variables

Required:

- `SERVICE_BASE_URL` — image-generation endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — image model id.

Optional:

- `PROMPT` — generation prompt (defaults to a known-good prompt).
- `OUTPUT_FILE` — destination path (defaults to `image.png`).

## Versions

### v1 — initial release
