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

Customer-facing Python example for HuggingFace sentence-transformers similarity endpoints (`source_sentence` + `sentences` payload). Returns a list of similarity scores.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release
