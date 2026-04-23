+++
preset_name = "smtp_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify SMTP server returns a 220 greeting on connect"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok" }
+++

# smtp / connectivity — SMTP banner smoke test

Bash smoke test for mail-submission services routed through the
UnitySVC SMTP relay. A healthy server answers a TCP connect with
`220 ... ESMTP ...` within five seconds; anything else is failure.

## Modes

- **Local** — harness sets `$HOST` and `$PORT` from
  `upstream_access_config`. `$PORT` defaults to 587 (submission).
- **Gateway** — harness sets `$SERVICE_BASE_URL` as `smtp://host:port`
  or `smtps://host:port`. The script strips the scheme, splits host
  from port, and defaults the port to 587 if absent.

The script picks the mode by looking at which env var is set — no
`local_testing` conditional needed.

## How the test works

1. Open a TCP connection via `nc -w 5` (5-second cap on both connect
   and idle-after-banner).
2. Send `QUIT` so the server closes cleanly instead of timing out on
   us.
3. Read the first line of output.
4. Accept any line starting with `220 `.

## Conventions

- Success line: `connectivity ok (220 ...)` — `meta.output_contains`
  uses `connectivity ok` so any banner text passes.
- Does not run `STARTTLS` or authenticate. This test is strictly
  "pipe opens and server says it's SMTP".
- Ports 25 and 465 work too; override `PORT` in the env.

## Versions

### v2 — TLS support

- Reads `$TLS` env var (local mode) and detects `smtps://` scheme (online
  mode) to select the transport.
- When TLS is required, uses `openssl s_client -connect` instead of `nc`
  so that implicit-TLS (SMTPS) upstreams complete the handshake before
  the server sends the `220` banner.
- When TLS is not required, behaviour is identical to v1.
- Use v2 for any upstream with `tls: true` in `upstream_access_config`
  or a `smtps://` gateway URL.

### v1 — initial release

- Uses `nc -w 5`; sends `QUIT`; accepts any `220 ...` banner.
- Plain SMTP only — does not handle implicit TLS (SMTPS).
