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

Curl-based POST to `/images/generations`; uses an inline
Python one-liner to base64-decode the result so the script does
not depend on `jq`.

## Environment variables

Required:

- `UNITYSVC_API_KEY` — bearer token.

Optional:

- `PROMPT` — generation prompt.
- `OUTPUT_FILE` — destination path (defaults to `image.png`).

## Versions

### v1 — initial release
