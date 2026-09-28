+++
preset_name = "llm_code_example_imagetoimage_requests"
category = "code_example"
mime_type = "python"
file = "code-example-imagetoimage.py.j2"
description = "Python example: image-to-image transform via Hugging Face /models/<model>"
is_active = true
is_public = true
meta = { variant = "Image to image", requirements = ["requests"], min_expected_metrics = { images_generated = 1 } }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "image-edit", dialect = "openai" }
+++

# llm / code-example-imagetoimage-requests — image-to-image via `requests`

Customer-facing Python example for HuggingFace-style image-to-image endpoints. Posts the input image as multipart with a prompt and strength parameter.

## Template variables (filled in by the platform when rendering for a given access interface)

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
- **Amended in 0.2.3**: `applies_to` now declares `dialect = "openai"`.
  It named only the capability, and an absent key means "no constraint" — so
  this example applied to callers writing any dialect, including ones whose
  upstream has no such endpoint. Selection metadata only: nothing this example
  does has changed, and every service that received it still does, because they
  all declare `openai`.
