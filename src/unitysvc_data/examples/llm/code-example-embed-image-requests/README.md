+++
preset_name = "llm_code_example_embed_image_requests"
category = "code_example"
mime_type = "python"
file = "code-example-embed-image.py.j2"
description = "Python example: embed an image via /embed (Cohere v2-style)"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-embed-image-requests — image embeddings via `requests`

Customer-facing Python example for `/embed` endpoints
that accept a base64 data-URI image (Cohere v2 / similar). Fetches
a public test image, inlines it as a data URI, and posts to the
gateway.

## Environment variables

Required:

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — image-embedding model id.

Optional:

- `IMAGE_URL` — alternate test image URL.

## Versions

### v1 — initial release
