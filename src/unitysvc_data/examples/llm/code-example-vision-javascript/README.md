+++
preset_name = "llm_code_example_vision_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-vision.js.j2"
description = "JavaScript example: describe an image via OpenAI-compatible /chat/completions vision messages"
is_active = true
is_public = true
+++

# llm / code-example-vision-javascript — vision via `fetch`

Customer-facing Node.js example for OpenAI-compatible
vision (multimodal chat) endpoints. Sends a text prompt plus an
image URL.

## Environment variables

Required:

- `SERVICE_BASE_URL` — chat completions endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — vision model id.

Optional:

- `IMAGE_URL` — alternate image URL.
- `PROMPT` — alternate prompt.

## Versions

### v1 — initial release
