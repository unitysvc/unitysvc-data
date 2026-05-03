+++
preset_name = "llm_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify an OpenAI-compatible LLM endpoint by issuing a tiny chat completion"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
parameters = { version_prefix = "/v1" }
+++

# llm / connectivity — chat completion smoke test

Connectivity check for OpenAI-compatible LLM services routed through
the UnitySVC LLM gateway. Posts a one-token chat completion against
`{{ routing_key.model }}`, asserts the gateway returned a real
`choices` array, and prints `connectivity ok` on success.

This is a step deeper than `api_connectivity` (which just checks the
URL responds). For an LLM service, "is the gateway alive?" is too
weak — what we actually want to know is "can this model produce a
completion?" The cheap one-token request answers that without
generating a real reply.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream key when wired as a secret (BYOK).

## Versions

### v1 — initial release

- POST `/chat/completions` with `messages: [{role: user, content: "ping"}]` and `max_tokens: 1`.
- `curl --fail-with-body` so 4xx / 5xx surface as non-zero exit + body in stderr.
- `grep -q '"choices"'` so a 200 with an unrelated body (rare, but
  some upstream errors return 200 with an `{"error": ...}` envelope)
  still fails.
- Output contains `connectivity ok` — paired with the
  `output_contains = "connectivity ok"` meta so the run-tests flow can
  confirm a real round-trip.
