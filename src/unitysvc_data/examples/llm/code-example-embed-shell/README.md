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

## Environment variables (all required)

- `SERVICE_BASE_URL` — embeddings endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

## Versions

### v1 — initial release

- `curl` POST with `model` + two-element `input` array.
- Heredoc JSON so no `jq` dependency is required.
- `${VAR:?msg}` guards on the three required env vars so a missing
  one fails before the request is sent.
- Plain shell script (no `.j2` suffix) — no Jinja2 expansion.
