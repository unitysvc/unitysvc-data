+++
preset_name = "llm_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: send a chat completion request to an OpenAI-compatible LLM via curl"
is_active = true
is_public = true
+++

# llm / code-example-shell — chat completion via `curl`

Customer-facing shell example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses `curl` and a
heredoc-built JSON payload so it works on any POSIX shell without
needing `jq`.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Versions

### v1 — initial release

- `curl` POST with `model` + two-message `messages` array.
- `${VAR:?msg}` guards on the three required env vars so a missing
  one fails before the request is sent.
- `set -e -o pipefail` so failures (including inside pipes)
  propagate.
