+++
preset_name = "llm_code_example_embed_image_requests"
category = "code_example"
mime_type = "python"
file = "code-example-embed-image.py.j2"
description = "Python example: embed an image via /embed (Cohere v2-style)"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-embed-image-requests — image embeddings via `requests`

Customer-facing Python example for `/embed` endpoints that accept a base64 data-URI image (Cohere v2 / similar). Fetches a public test image, inlines it as a data URI, and posts to the gateway.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL` — alternate test image URL.

## Versions

### v1 — initial release
