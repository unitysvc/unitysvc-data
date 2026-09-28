+++
preset_name = "api_code_example_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: GET an HTTP endpoint via the requests library and assert a 2xx response"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# api / code-example-requests — generic HTTP smoke test via `requests`

Customer-facing Python example for any HTTP-based service that's
fronted by a UnitySVC gateway (HTTP relays, S3-compatible proxies,
echo services, simple forward services). Sends a `GET` to
`{{ service_base_url }}` using the `requests` library and asserts
the response is 2xx.

Companion to `api_connectivity` (curl smoke test, internal) — same
endpoint check, different audience: this one is the doc you'd hand
a customer who wants to wire the service into their own Python code.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — optional. Sent as `Authorization: Bearer …` when set.

## Versions

### v1 — initial release

- `GET {{ service_base_url }}` with optional bearer auth, 5-second timeout.
- `raise_for_status()` raises on any non-2xx response (exit code ≠ 0).
- Prints `ok` after `raise_for_status()` confirms a successful endpoint hit.
- **Amended in 0.2.2**: verification moved into the script. The runner-side
  `output_contains` sentinel it used to rely on was retired platform-side
  (unitysvc/unitysvc#2490), so the check is now a real status or
  response-shape assertion, wrapped in `{%- if not customer_display %}` to keep
  it out of the published example. The unconditional success marker is gone.

