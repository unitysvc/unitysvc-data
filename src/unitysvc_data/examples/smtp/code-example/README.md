+++
preset_name = "smtp_code_example"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send an email through the SMTP relay using smtplib"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
+++

# smtp / code-example — SMTP relay Python example

Customer-facing primary example for SMTP relay services. Composes a
test email and delivers it through the SMTP relay using Python's
standard `smtplib`. Supports both direct upstream (local-test mode)
and gateway-routed (customer mode) delivery.

## Branches

| `local_testing` | Behaviour |
|-----------------|-----------|
| `true`          | Connects directly to the upstream SMTP server using `HOST`, `PORT`, `USERNAME`, and `PASSWORD` env vars. |
| `false`         | Parses `SERVICE_BASE_URL` (`smtp://host:port` or `smtps://host:port`) and authenticates with `UNITYSVC_API_KEY`. |

## Environment variables (local mode)

- `HOST` — SMTP server hostname; set by the harness from
  `upstream_access_config`.
- `PORT` — SMTP port; defaults to 587.
- `USERNAME`, `PASSWORD` — SMTP credentials (optional).

## Environment variables (gateway mode)

- `SERVICE_BASE_URL` — form `smtp://host:port` or `smtps://host:port`.
- `UNITYSVC_API_KEY` — gateway authentication key, used as the SMTP
  password.

## Conventions

- Ends with `print("connectivity ok")` after successful send so the
  example functions as a deliverability smoke test.
- Uses STARTTLS when available in plain-SMTP mode; uses `SMTP_SSL` for
  `smtps://` scheme.

## Note on test skipping

SMTP code examples that cannot reach a live mail server should use
`meta.skip_test = true` in the listing document entry. This preset
assumes a reachable SMTP server is available in the test environment.

## Versions

### v1 — initial release

- Two-branch rendering on `local_testing`.
- Detects implicit TLS from `smtps://` scheme and `use_ssl` env var.
- Attempts STARTTLS when the server advertises support.
