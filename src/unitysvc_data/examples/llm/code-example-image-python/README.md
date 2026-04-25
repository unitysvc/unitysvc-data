+++
preset_name = "llm_code_example_image_python"
category = "code_example"
mime_type = "python"
file = "code-example-image.py.j2"
description = "Python example: generate an image from a text prompt via an OpenAI-compatible images endpoint"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-image-python — text-to-image

Customer-facing Python example for OpenAI-compatible
`/v1/images/generations`-shaped endpoints. Sends a prompt and saves
the returned image to disk.

## Environment variables

- `SERVICE_BASE_URL` — image-generation endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.
- `PROMPT` — optional; defaults to a recognisable test prompt.
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
