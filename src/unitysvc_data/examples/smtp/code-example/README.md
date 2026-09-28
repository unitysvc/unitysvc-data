+++
preset_name = "smtp_code_example"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a test email via the UnitySVC SMTP gateway"
is_active = true
is_public = true
+++

# smtp / code-example — send-email smoke test

Customer-facing Python example for SMTP services routed through the
UnitySVC gateway (BYOK relay, multi-enrollment relay, mailpit-backed
test gateway). Composes a one-line text email and sends it, picking
implicit TLS (SMTPS) vs plain-with-STARTTLS based on the rendered URL
or the seller's `tls` flag.

The same template covers both render modes — local-testing
(`local_testing == True`) inlines the seller's upstream credentials
for ops-test runs, gateway mode parses `service_base_url` and reads
the customer's API key from `UNITYSVC_API_KEY`.

## Template variables

**Local-testing mode** (`{% raw %}{% if local_testing %}{% endraw %}`) — the renderer fills these
from the offering's `upstream_access_config` after substituting
`ops_testing_parameters`:

- `{% raw %}{{ host }}{% endraw %}` — upstream SMTP host.
- `{% raw %}{{ port }}{% endraw %}` — upstream SMTP port. Defaults to 587 (submission).
- `{% raw %}{{ tls }}{% endraw %}` — `true` ⇒ implicit TLS (port 465 / SMTPS),
  `false` ⇒ plain TCP with optional STARTTLS upgrade. Accepted as
  Python bool, lowercase string, or capitalised string.
- `{% raw %}{{ username }}{% endraw %}`, `{% raw %}{{ password }}{% endraw %}` — upstream credentials. Inlining
  these is fine because this branch is only ever rendered for the
  seller's own ops-test flow; customers never see local-testing
  output.

**Gateway mode** (the `else` branch) — the renderer fills these from
the listing's access interface:

- `{% raw %}{{ service_base_url }}{% endraw %}` — `smtp://host:port` or
  `smtps://host:port`.
- `{% raw %}{{ routing_key.username }}{% endraw %}` — SMTP username (per the listing's
  `routing_key`).

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — gateway-mode SMTP password. Always pulled from
  env, never inlined into rendered output (per-customer secret).

## Versions

### v1 — initial release

- Implicit TLS via `smtplib.SMTP_SSL` when `use_ssl`; otherwise plain
  `smtplib.SMTP` with optional STARTTLS upgrade detected via
  `server.has_extn("STARTTLS")`.
- 10-second connect/operation timeout.
- Prints `connectivity ok` after `send_message()` completes successfully;
  SMTP and transport failures exit non-zero.
- **Amended in 0.2.2**: verification moved into the script. The runner-side
  `output_contains` sentinel it used to rely on was retired platform-side
  (unitysvc/unitysvc#2490), so the check is now a real status or
  response-shape assertion, wrapped in `{%- if not customer_display %}` to keep
  it out of the published example. The unconditional success marker is gone.

