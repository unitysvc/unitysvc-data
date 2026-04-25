+++
preset_name = "recommender_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: submit feedback and fetch personalized recommendations from a Gorse-shaped recommender via curl"
is_active = true
is_public = true
+++

# recommender / code-example-shell — feedback + recommend round-trip (curl)

Customer-facing shell variant of `recommender_code_example_python`.
POSTs a feedback event to `/api/feedback`, then GETs five
recommendations from `/api/recommend/<user>`.

## Environment variables

- `SERVICE_BASE_URL` — recommender base URL.
- `USER_ID` — user id, defaults to `demo-user`.
- `GORSE_API_KEY` (local) or `UNITYSVC_API_KEY` (gateway).

## Versions

### v1 — initial release

- Two `curl` calls; status codes captured via `-w '%{http_code}'`.
- `set -e` + per-call status check so non-200 fails the script.
- Renders different auth headers for local vs gateway mode.
