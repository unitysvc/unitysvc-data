+++
preset_name = "llm_code_example_image_requests"
category = "code_example"
mime_type = "python"
file = "code-example-image.py.j2"
description = "Python example: generate an image from a text prompt via an OpenAI-compatible images endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-image-requests — text-to-image via `requests`

Customer-facing Python example for OpenAI-compatible
`/v1/images/generations`-shaped endpoints. Sends a prompt and saves
the returned image to disk.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `PROMPT` — defaults to a recognisable test prompt.
- `OUTPUT_FILE` — destination path. Defaults to `image.png`.

## Conventions

- Requests `b64_json` so the script gets the bytes inline rather than
  needing to follow a signed URL — easier to run in CI without
  outbound network access for the second hop.
- Falls back to printing the URL or the raw body when the provider
  returns a non-OpenAI shape.

## Versions

### v1 — initial release

- POST `model` + `prompt` + `size=1024x1024` + `response_format=b64_json`.
- Saves the decoded image to `OUTPUT_FILE`.
- Required env vars fail fast with `KeyError` if missing.
