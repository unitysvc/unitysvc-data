+++
preset_name = "llm_code_example_embed_image_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-embed-image.js.j2"
description = "JavaScript example: embed an image via /embed (Cohere v2-style)"
is_active = true
is_public = true
+++

# llm / code-example-embed-image-javascript — image embeddings via `fetch`

Customer-facing Node.js example for `/embed` endpoints that accept a base64 data-URI image. Inlines the image as a data URI before posting.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL` — alternate test image URL.

## Versions

### v1 — initial release
