+++
preset_name = "recommender_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: submit feedback and fetch personalized recommendations from a Gorse-shaped recommender"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# recommender / code-example-python — feedback + recommend round-trip

Customer-facing Python example for Gorse-shaped recommender services
routed through the UnitySVC recommender gateway. The script:

1. Submits a `like` feedback event for `item-1` (so the engine has at
   least one signal to work with).
2. Asks for five personalized recommendations for `USER_ID`.

## Modes

The Jinja2 template branches on `local_testing`:

| Mode | Auth header |
|------|-------------|
| local | `X-API-Key: $GORSE_API_KEY` |
| gateway | `Authorization: Bearer $UNITYSVC_API_KEY` |

## Environment variables

- `SERVICE_BASE_URL` — recommender base URL.
- `USER_ID` — the user the feedback / recommendation is for. Defaults
  to `demo-user`.
- `GORSE_API_KEY` (local) or `UNITYSVC_API_KEY` (gateway).

## Versions

### v1 — initial release

- POSTs feedback to `/api/feedback`, GETs recommendations from
  `/api/recommend/<user>?n=5`.
- Surfaces non-200 status codes on stderr and exits 1.
