+++
preset_name = "llm_code_example_vision_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-vision.js.j2"
description = "JavaScript example: describe an image via OpenAI-compatible /chat/completions vision messages"
is_active = true
is_public = true
meta = { variant = "Vision" }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "image-text-to-text", dialect = "openai", upstream = "openai", feature = "vision" }
+++

# llm / code-example-vision-javascript — vision via `fetch`

Customer-facing Node.js example for OpenAI-compatible vision (multimodal chat) endpoints. Sends a text prompt plus an image URL.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL` — alternate image URL.
- `PROMPT` — alternate prompt.

## Versions

### v1 — initial release

### v2 — inline the image, and assert the reply shape

- Fetches `IMAGE_URL` and sends it as a `data:` URI, so the request no
  longer depends on the provider being able to reach that host.
  Server-side fetching was intermittently failing (observed on DeepSeek:
  3 of 4 identical calls succeeded, the fourth returned
  `400 Failed to download image`), which made every vision example a
  coin-flip in CI for reasons unrelated to the service.
- Takes the media type from the image response's `content-type` rather
  than assuming JPEG.
- Adds the `choices` assertion and the `example ok` sentinel the family
  metadata already expects — a 200 carrying an error object no longer
  reads as a pass.
