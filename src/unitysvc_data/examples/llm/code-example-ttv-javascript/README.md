+++
preset_name = "llm_code_example_ttv_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-ttv.js.j2"
description = "JavaScript example: text-to-video via HF /models/<model>"
is_active = true
is_public = true
+++

# llm / code-example-ttv-javascript — text-to-video via `fetch`

Customer-facing Node.js example for HuggingFace text-to-video endpoints. Writes the returned binary video to disk.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `PROMPT`, `OUTPUT_FILE`.

## Versions

### v1 — initial release
