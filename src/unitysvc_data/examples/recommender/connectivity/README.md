+++
preset_name = "recommender_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify a Gorse-shaped recommender endpoint is reachable and returns a JSON array"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# recommender / connectivity — Gorse smoke test

Bash smoke test for recommender services exposing a Gorse-style HTTP
API (`/api/recommend/<user>`). The script asks for a single
recommendation for a throwaway user id and accepts any JSON array as
"alive" — Gorse returns `[]` for unknown users rather than an error,
so we don't need a pre-seeded fixture in the gateway.

## Modes

The Jinja2 template branches on `local_testing`:

| Mode | Auth header |
|------|-------------|
| local | `X-API-Key: $GORSE_API_KEY` (direct upstream) |
| gateway | `Authorization: Bearer $UNITYSVC_API_KEY` |

## Environment variables

- `SERVICE_BASE_URL` — recommender base URL.
- `GORSE_API_KEY` (local mode) or `UNITYSVC_API_KEY` (gateway mode).

## Versions

### v1 — initial release

- `curl --max-time 5` against `/api/recommend/connectivity-test?n=1`.
- Asserts the response body starts with `[` so empty arrays still
  pass.
- Renders different auth headers for local vs gateway mode.
