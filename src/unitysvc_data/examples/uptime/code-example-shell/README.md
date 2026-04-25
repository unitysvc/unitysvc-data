+++
preset_name = "uptime_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: trigger an uptime check on the bridge endpoint via curl"
is_active = true
is_public = true
+++

# uptime / code-example-shell — trigger an uptime check (curl)

Customer-facing shell variant of `uptime_code_example_python`.
POSTs an empty body in gateway mode (the bridge already has the
check parameters from the enrollment) or the rendered
`ops_testing_parameters` in local-testing mode.

## Environment variables

- `SERVICE_BASE_URL` — bridge endpoint.
- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release

- `curl POST` with `Authorization: Bearer …` and a JSON body that
  branches on `local_testing`.
- `set -e` so the script fails on non-2xx responses.
