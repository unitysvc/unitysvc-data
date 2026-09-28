+++
preset_name = "api_code_example_shell"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "curl example: GET an HTTP endpoint and assert a 2xx response"
is_active = true
is_public = true
+++

# api / code-example-shell — generic HTTP smoke test via `curl`

Customer-facing shell example for any HTTP-based service fronted by
a UnitySVC gateway. `curl`s `{{ service_base_url }}` and asserts a
2xx status.

Companion to `api_connectivity` (which has broader pass criteria —
2xx/3xx/401/403 — and is intended for internal connectivity testing).
This preset is stricter (2xx only) and is the doc you'd show a
customer wiring the service into a shell script.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — optional. Sent as `Authorization: Bearer …` when set.

## Versions

### v1 — initial release

- `curl -fsS {{ service_base_url }}` with optional bearer auth, 5-second timeout.
- `-f` makes curl exit non-zero on any non-2xx response.
- Prints `ok` after curl confirms a successful endpoint hit.
- **Amended in 0.2.2**: verification moved into the script. The runner-side
  `output_contains` sentinel it used to rely on was retired platform-side
  (unitysvc/unitysvc#2490), so the check is now a real status or
  response-shape assertion, wrapped in `{%- if not customer_display %}` to keep
  it out of the published example. The unconditional success marker is gone.

