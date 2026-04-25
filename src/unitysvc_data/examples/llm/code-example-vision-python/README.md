+++
preset_name = "llm_code_example_vision_python"
category = "code_example"
mime_type = "python"
file = "code-example-vision.py.j2"
description = "Python example: ask a vision-capable LLM about a local image"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-vision-python — image understanding

Customer-facing Python example for vision-capable LLMs exposed
through the OpenAI-compatible chat-completion route. The image is
inlined as a base64 `data:` URL inside an `image_url` content block,
which is the format every OpenAI-compatible vision model accepts.

## Environment variables

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.
- `IMAGE_FILE` — path to a local image. Defaults to `image.jpg`.
- `PROMPT` — optional caption query. Defaults to "Describe this image."

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
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL`, `IMAGE_FILE`,
  `PROMPT` from env.
