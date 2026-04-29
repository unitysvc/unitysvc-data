+++
preset_name = "llm_code_example_sentencetransformers_requests"
category = "code_example"
mime_type = "python"
file = "code-example-sentencetransformers.py.j2"
description = "Python example: sentence-similarity via HF sentence-transformers /models/<model>"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-sentencetransformers-requests — sentence similarity via `requests`

Customer-facing Python example for HuggingFace
sentence-transformers similarity endpoints (`source_sentence` +
`sentences` payload). Returns a list of similarity scores.

## Environment variables (all required)

- `SERVICE_BASE_URL`, `UNITYSVC_API_KEY`, `MODEL`.

## Versions

### v1 — initial release
