+++
preset_name = "llm_code_example_embed_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-embed.sh.j2"
description = "Shell example: request OpenAI-compatible embeddings via curl"
is_active = true
is_public = true
+++

# llm / code-example-embed-shell — embeddings via `curl`

Customer-facing shell example for OpenAI-compatible embedding
endpoints. Sends two short strings as `input` and prints the raw
JSON response.

## Environment variables

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.

## Versions

### v1 — initial release

- `curl` POST with `model` + two-element `input` array.
- Heredoc JSON so no `jq` dependency is required.
