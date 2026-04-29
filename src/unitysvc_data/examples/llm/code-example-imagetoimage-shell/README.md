+++
preset_name = "llm_code_example_imagetoimage_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-imagetoimage.sh.j2"
description = "Bash example: image-to-image transform via Hugging Face /models/<model> using curl"
is_active = true
is_public = true
+++

# llm / code-example-imagetoimage-shell — image-to-image via `curl`

Curl-based POST to a HuggingFace-style image-to-image endpoint. Downloads a sample image first if missing.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL`, `PROMPT`, `STRENGTH`, `OUTPUT_FILE`.

## Versions

### v1 — initial release
