+++
preset_name = "llm_code_example_vision_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-vision.sh.j2"
description = "Bash example: describe an image via OpenAI-compatible /chat/completions using curl"
is_active = true
is_public = true
+++

# llm / code-example-vision-shell — vision via `curl`

Curl-based POST to `/chat/completions` with a multimodal
content array (text + image_url).

## Environment variables

Required:

- `UNITYSVC_API_KEY` — bearer token.

Optional:

- `IMAGE_URL`, `PROMPT`.

## Versions

### v1 — initial release
