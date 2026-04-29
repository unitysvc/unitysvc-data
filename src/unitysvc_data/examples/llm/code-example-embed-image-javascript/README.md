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

Customer-facing Node.js example for `/embed` endpoints
that accept a base64 data-URI image. Inlines the image as a data
URI before posting.

## Environment variables

Required:

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — image-embedding model id.

Optional:

- `IMAGE_URL` — alternate test image URL.

## Versions

### v1 — initial release
