+++
preset_name = "llm_code_example_embed_image_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-embed-image.sh.j2"
description = "Bash example: embed an image via /embed (Cohere v2-style) using curl"
is_active = true
is_public = true
+++

# llm / code-example-embed-image-shell — image embeddings via `curl`

Curl-based POST to `/embed` with a base64-inlined image
data-URI.

## Environment variables

Required:

- `UNITYSVC_API_KEY` — bearer token.

Optional:

- `IMAGE_URL` — alternate test image URL.

## Versions

### v1 — initial release
