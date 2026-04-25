+++
preset_name = "notification_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "Shell example: publish a push notification through a ntfy-shaped notification gateway"
is_active = true
is_public = true
+++

# notification / code-example-shell — ntfy publish via curl

Customer-facing shell variant of `notification_code_example_python`.
Posts a one-line text body with `Title`, `Priority`, and `Tags`
headers — the format every ntfy server understands.

## Environment variables

- `SERVICE_BASE_URL` — full publish URL including the topic.
- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release

- `curl POST` with metadata headers and a plain-text body.
- `set -e` so non-2xx fails the script.
