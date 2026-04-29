+++
preset_name = "llm_code_example_rerank_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-rerank.sh.j2"
description = "Bash example: rerank documents via /rerank using curl"
is_active = true
is_public = true
+++

# llm / code-example-rerank-shell — document reranking via `curl`

Curl-based POST to `/rerank` with a small fixed query+documents list.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release
