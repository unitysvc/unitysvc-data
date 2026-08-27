+++
preset_name = "llm_code_example_vision_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-vision.sh.j2"
description = "Bash example: describe an image via OpenAI-compatible /chat/completions using curl"
is_active = true
is_public = true
meta = { variant = "Vision", output_contains = "example ok" }
parameters = { version_prefix = "/v1" }
applies_to = { capability = "image-text-to-text", dialect = "openai", upstream = "openai", feature = "vision" }

[versions.v1]
# v1 predates the response-shape assertion and prints no sentinel.
meta = { output_contains = "" }
+++

# llm / code-example-vision-shell — vision via `curl`

Curl-based POST to `/chat/completions` with a multimodal content array (text + image_url).

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

Optional:

- `IMAGE_URL`, `PROMPT`.

## Versions

### v1 — initial release

### v3 — inline the image instead of asking the model to fetch it

- Downloads `IMAGE_URL` with `curl` and sends it as a `data:` URI, so the
  request no longer depends on the provider being able to reach that host.
  Server-side fetching was intermittently failing (observed on DeepSeek:
  3 of 4 identical calls succeeded, the fourth returned
  `400 Failed to download image`), which made every vision example a
  coin-flip in CI for reasons unrelated to the service.
- Takes the media type from the response's `Content-Type` rather than
  assuming JPEG, so swapping in a PNG needs no edit.
- `base64` wraps output on GNU but not BSD; `tr -d '\n'` normalises both.
