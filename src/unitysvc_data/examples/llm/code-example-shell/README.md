+++
preset_name = "llm_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh"
description = "Shell example: send a chat completion request to an OpenAI-compatible LLM via curl"
is_active = true
is_public = true
+++

# llm / code-example-shell — chat completion via `curl`

Customer-facing shell example for OpenAI-compatible chat completion
services routed through the UnitySVC LLM gateway. Uses `curl` and a
heredoc-built JSON payload so it works on any POSIX shell without
needing `jq`.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

## Versions

### v1 — initial release

- `curl` POST with `model` + two-message `messages` array.
- `${VAR:?msg}` guards on the three required env vars so a missing
  one fails before the request is sent.
- `set -e -o pipefail` so failures (including inside pipes)
  propagate.
- Plain shell script (no `.j2` suffix) — no Jinja2 expansion.
