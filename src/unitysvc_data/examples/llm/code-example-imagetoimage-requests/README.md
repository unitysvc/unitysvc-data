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

Customer-facing Python example for HuggingFace-style
image-to-image endpoints. Posts the input image as multipart with
a prompt and strength parameter.

## Environment variables

Required:

- `SERVICE_BASE_URL`, `UNITYSVC_API_KEY`, `MODEL`.

Optional:

- `IMAGE_URL` — input image (defaults to a Wikimedia cat photo).
- `PROMPT`, `STRENGTH`, `OUTPUT_FILE`.

## Versions

### v1 — initial release
