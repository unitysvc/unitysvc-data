+++
preset_name = "llm_code_example_imagetoimage_requests"
category = "code_example"
mime_type = "python"
file = "code-example-imagetoimage.py.j2"
description = "Python example: image-to-image transform via Hugging Face /models/<model>"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-imagetoimage-requests — image-to-image via `requests`

Customer-facing Python example for HuggingFace-style image-to-image endpoints. Posts the input image as multipart with a prompt and strength parameter.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL` — input image (defaults to a Wikimedia cat photo).
- `PROMPT`, `STRENGTH`, `OUTPUT_FILE`.

## Versions

### v1 — initial release
