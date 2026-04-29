+++
preset_name = "llm_code_example_guard_shell"
category = "code_example"
mime_type = "bash"
file = "code-example-guard.sh.j2"
description = "Bash example: send an unsafe prompt to a guard/safety model via curl"
is_active = true
is_public = true
+++

# llm / code-example-guard-shell — safety guard probe via `curl`

Curl-based POST to `/chat/completions` with a known-unsafe prompt; useful for demonstrating that a guard model returns the expected refusal/classification.

## Template variables (substituted by the platform at upload time)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release
