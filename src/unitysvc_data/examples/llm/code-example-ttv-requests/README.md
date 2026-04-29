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

Customer-facing Python example for HuggingFace text-to-video endpoints. Writes the returned binary video to disk.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `PROMPT`, `OUTPUT_FILE` (defaults to `output.mp4`).

## Versions

### v1 — initial release
