+++
preset_name = "http_relay_code_example"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send an HTTP request through the relay using requests"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok", requirements = ["requests"] }
+++

# http / code-example — HTTP relay Python example

Customer-facing primary example for HTTP relay services. Sends a GET
request to the upstream endpoint (via the gateway or directly in test
mode) and prints the response status.

## Branches

| `local_testing` | Behaviour |
|-----------------|-----------|
| `true`          | Connects directly to upstream using `HTTP_RELAY_BASE_URL` and optional `HTTP_RELAY_API_KEY`. |
| `false`         | Routes through the UnitySVC HTTP gateway via `SERVICE_BASE_URL`. Falls back to the echo staging endpoint if the URL is empty or contains unrendered template syntax. |

## Environment variables (local mode)

- `HTTP_RELAY_BASE_URL` — upstream endpoint URL; defaults to the echo
  staging endpoint.
- `HTTP_RELAY_API_KEY` — optional upstream API key.

## Environment variables (gateway mode)

- `SERVICE_BASE_URL` — gateway URL; falls back to echo staging endpoint
  when empty or when it contains unresolved template syntax (e.g.,
  `enrollment_vars.code` for multi-enrollment services).

## Conventions

- Ends with `print("connectivity ok")` so the example also functions
  as a smoke test.

## Versions

### v1 — initial release

- Two-branch rendering on `local_testing`.
- Graceful fallback for unresolved multi-enrollment gateway URLs.
