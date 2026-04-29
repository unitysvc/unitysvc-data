+++
preset_name = "llm_code_example_guard_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example-guard.js.j2"
description = "JavaScript example: send an unsafe prompt to a guard/safety model via /chat/completions"
is_active = true
is_public = true
+++

# llm / code-example-guard-javascript — safety guard probe via `fetch`

Customer-facing Node.js example for guard/safety classifier models served behind an OpenAI-compatible `/chat/completions` endpoint. Sends a known-unsafe prompt so the response demonstrates the classifier's verdict.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release
