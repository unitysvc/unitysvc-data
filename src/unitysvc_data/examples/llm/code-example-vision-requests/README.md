+++
preset_name = "llm_code_example_vision_requests"
category = "code_example"
mime_type = "python"
file = "code-example-vision.py.j2"
description = "Python example: ask a vision-capable LLM about a publicly-hosted image"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-vision-requests — image understanding via `requests`

Customer-facing Python example for vision-capable LLMs exposed
through the OpenAI-compatible chat-completion route. Sends an
`image_url` content block referencing a publicly-hosted image, so
the script runs standalone without any local fixture.

## Environment variables

Required:

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier.

Optional:

- `IMAGE_URL` — public URL of the image. Defaults to a 280 KB cat
  photo on Wikimedia Commons. Override with any publicly-reachable
  jpeg / png / webp.
- `PROMPT` — caption query. Defaults to "Describe this image."

## Conventions

- Sends the URL straight through in the `image_url` block. The
  model server fetches it. This is the simplest path for most
  customers.
- Air-gapped or offline-first deployments where the model server
  can't reach the public internet should base64-inline the image
  instead — switch the `image_url` value to a `data:image/jpeg;base64,...`
  string.

## Versions

### v1 — initial release

- Chat-completion POST with a multimodal `content` array (text +
  image_url referencing a public Wikimedia Commons photo by
  default).
- `response.raise_for_status()` so non-2xx exits non-zero.
