+++
preset_name = "llm_code_example_ttv_requests"
category = "code_example"
mime_type = "python"
file = "code-example-ttv.py.j2"
description = "Python example: text-to-video via HF /models/<model>"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-ttv-requests — text-to-video via `requests`

Customer-facing Python example for HuggingFace
text-to-video endpoints. Writes the returned binary video to disk.

## Environment variables

Required:

- `SERVICE_BASE_URL`, `UNITYSVC_API_KEY`, `MODEL`.

Optional:

- `PROMPT`, `OUTPUT_FILE` (defaults to `output.mp4`).

## Versions

### v1 — initial release
