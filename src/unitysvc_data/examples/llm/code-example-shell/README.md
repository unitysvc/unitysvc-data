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

## Environment variables

- `SERVICE_BASE_URL` — chat-completion endpoint (gateway URL or
  upstream URL in local-testing mode).
- `UNITYSVC_API_KEY` — sent as `Authorization: Bearer …`.
- `MODEL` — optional override. Defaults to the listing's
  `offering.name`, rendered at upload time.

## Versions

### v1 — initial release

- `curl` POST with `model` + two-message `messages` array.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from the
  environment.
- `set -o pipefail` so failures inside pipes propagate.
