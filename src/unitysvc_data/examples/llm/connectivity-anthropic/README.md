+++
preset_name = "llm_connectivity_anthropic"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify an Anthropic-Messages-API LLM endpoint by issuing a tiny one-token message"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# llm / connectivity-anthropic — Anthropic Messages API smoke test

Connectivity check for Anthropic-Messages-API LLM services
(`/v1/messages`, primarily Claude-family models). Companion to
`llm_connectivity` (OpenAI-compatible `/chat/completions`) — Anthropic's
API isn't OpenAI-shaped (different endpoint, required `max_tokens`,
top-level `system`, `content[].text` response), so it needs its own
preset.

## Differences vs `llm_connectivity`

| | `llm_connectivity` | `llm_connectivity_anthropic` |
|---|---|---|
| Endpoint | `/chat/completions` | `/v1/messages` |
| Auth header | `Authorization: Bearer …` | `x-api-key: …` |
| Required header | — | `anthropic-version: 2023-06-01` |
| Required body fields | `model`, `messages` | `model`, `messages`, `max_tokens` |
| Response shape | `"choices"` | `"content"` |

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Sent as the `x-api-key` header.
  Customer's svcpass for gateway access, or an upstream key when
  wired as a secret (BYOK).

## Versions

### v1 — initial release

- POST `/v1/messages` with `messages: [{role: user, content: "ping"}]`
  and `max_tokens: 1`.
- Sends `anthropic-version: 2023-06-01` (the version pinned by the
  current Python SDK; matches what gateways and Claude apps expect).
- `curl --fail-with-body` so 4xx / 5xx exit non-zero with the body
  on stderr.
- `grep -q '"content"'` — Anthropic returns the assistant text in a
  `content` array, so this confirms a real response envelope rather
  than a 200 with an unrelated body.
- Output contains `connectivity ok` — paired with the
  `output_contains = "connectivity ok"` meta so the run-tests flow
  can confirm a real round-trip.
