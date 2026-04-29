+++
preset_name = "llm_code_example_image_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-image.sh.j2"
description = "Bash example: generate an image via OpenAI-compatible /images/generations using curl"
is_active = true
is_public = true
+++

# llm / code-example-image-shell — image generation via `curl`

Curl-based POST to `/images/generations`; uses an inline Python one-liner to base64-decode the result so the script does not depend on `jq`.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `PROMPT` — generation prompt.
- `OUTPUT_FILE` — destination path (defaults to `image.png`).

## Versions

### v1 — initial release
