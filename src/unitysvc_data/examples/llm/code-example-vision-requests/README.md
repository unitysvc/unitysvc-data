+++
preset_name = "llm_code_example_vision_requests"
category = "code_example"
mime_type = "python"
file = "code-example-vision.py"
description = "Python example: ask a vision-capable LLM about a local image"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-vision-requests — image understanding via `requests`

Customer-facing Python example for vision-capable LLMs exposed
through the OpenAI-compatible chat-completion route. The image is
inlined as a base64 `data:` URL inside an `image_url` content block,
which is the format every OpenAI-compatible vision model accepts.

## Environment variables

Required:

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

Optional:

- `IMAGE_FILE` — path to a local image. Defaults to `image.jpg`.
- `PROMPT` — caption query. Defaults to "Describe this image."

## Conventions

- Inlines the image rather than sending a public URL so the example
  works in environments without outbound HTTP access for the second
  hop.
- Assumes JPEG (`image/jpeg`); update the `data:` MIME prefix if you
  pass a PNG.

## Versions

### v1 — initial release

- Chat-completion POST with multimodal `content` array (text +
  image_url).
- Required env vars fail fast with `KeyError` if missing.
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
