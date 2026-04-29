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

Curl-based POST to `/chat/completions` with a known-unsafe
prompt; useful for demonstrating that a guard model returns the
expected refusal/classification.

## Environment variables (required)

- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release
