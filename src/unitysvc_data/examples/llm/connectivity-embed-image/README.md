+++
preset_name = "llm_connectivity_embed_image"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity-embed-image.sh.j2"
description = "Verify a Cohere-shape image embedding endpoint by sending a tiny known image"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
parameters = { version_prefix = "/v2" }
+++

# llm / connectivity-embed-image — image embedding smoke test

Connectivity check for image-embedding services that speak the
**Cohere-shape** request body (`input_type=image`, base64-encoded
`images` array).  Cohere's OpenAI-compatibility layer's
`/embeddings` endpoint rejects image input, so image-embed services
have to hit the native `/v2/embed` path with the Cohere payload.

Downloads a tiny cat image to the OS temp dir, base64-inlines it as a
`data:` URI, POSTs to `/v2/embed`, asserts the response contains an
`embeddings` field, prints `connectivity ok` on success.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Parameters (per-listing)

- `version_prefix` (default `/v2`) — path segment between
  `service_base_url` and `/embed`.  Default matches Cohere's native
  v2 endpoint; override per-listing if a provider exposes the same
  shape under a different prefix.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required.

## Versions

### v1 — initial release

- Downloads cat sample image into `${TMPDIR:-/tmp}` if not already cached.
- Base64-encodes as a `data:image/jpeg;base64,...` URI.
- POST `/embed` (Cohere shape) with `model`, `input_type=image`,
  `embedding_types=[float]`, `images=[<data_uri>]`.
- Captures HTTP status separately so the response body can be surfaced
  on failure (the bare `--fail-with-body | grep -q` pattern eats the
  body and leaves operators with just an exit code).
- Output contains `connectivity ok` on success.
