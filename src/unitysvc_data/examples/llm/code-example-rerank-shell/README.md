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

Curl-based POST to `/rerank` with a small fixed
query+documents list.

## Environment variables (required)

- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release
