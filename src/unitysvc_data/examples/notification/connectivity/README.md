+++
preset_name = "notification_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify a ntfy-shaped notification endpoint accepts a published message"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# notification / connectivity — ntfy publish smoke test

Bash smoke test for push-notification services that speak the ntfy
publish protocol. Publishes a one-line text message to the
enrollment's topic URL (`SERVICE_BASE_URL` already includes the
topic) and verifies the JSON response carries `"event":"message"`,
which ntfy returns on a successful publish.

## Environment variables

- `SERVICE_BASE_URL` — full publish URL including the topic.
- `UNITYSVC_API_KEY` — bearer token.

## Versions

### v1 — initial release

- POST a `text/plain` body of `unitysvc connectivity test`.
- 5-second timeout.
- Asserts `"event":"message"` in the response (ntfy success shape).
