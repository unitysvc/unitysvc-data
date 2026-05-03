+++
preset_name = "llm_code_example_vision_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-vision.sh.j2"
description = "Bash example: describe an image via OpenAI-compatible /chat/completions using curl"
is_active = true
is_public = true
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-vision-shell — vision via `curl`

Curl-based POST to `/chat/completions` with a multimodal content array (text + image_url).

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL`, `PROMPT`.

## Versions

### v1 — initial release
