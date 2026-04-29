+++
preset_name = "llm_code_example_rerank_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-rerank.js.j2"
description = "JavaScript example: rerank documents via /rerank"
is_active = true
is_public = true
+++

# llm / code-example-rerank-javascript — document reranking via `fetch`

Customer-facing Node.js example for `/rerank` endpoints
(Cohere-style). Sends a small fixed query+documents list so the
output exercises the ranking path.

## Environment variables (all required)

- `SERVICE_BASE_URL` — rerank endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — rerank model id.

## Versions

### v1 — initial release
