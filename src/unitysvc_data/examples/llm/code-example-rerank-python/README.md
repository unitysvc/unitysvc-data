+++
preset_name = "llm_code_example_rerank_python"
category = "code_example"
mime_type = "python"
file = "code-example-rerank.py.j2"
description = "Python example: rerank a candidate document set against a query"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-rerank-python — rerank

Customer-facing Python example for rerank endpoints (Cohere-style
`/v2/rerank` payload: `query` + `documents` → ranked indices with
relevance scores).

## Environment variables

- `SERVICE_BASE_URL` — rerank endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.

## Conventions

- Sends a five-document candidate set with one obvious correct
  answer, so even a low-quality reranker is easy to assert against.
- Prints the raw response — the field set differs between providers
  (`results` vs `documents`), so leave parsing to the caller.

## Versions

### v1 — initial release

- POST `model` + `query` + `top_n` + `documents`.
