+++
preset_name = "msg_to_gateway_code_example_py"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) code example for gateway-transformer notification services"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { channel = "gateway" }
+++

# msg-to-gateway / code-example-py

Python (httpx) code example for gateway *transformer* channels — channels that
transform a canonical message envelope `{title, body, type, format}` into the
upstream provider's native payload **inside the gateway** and POST it directly
upstream, bypassing Apprise.

The transformer channel is selected at request time by appending `@<channel>` to
the service base URL (e.g. `@gateway`, `@gateway-plus`).

## Gateway mode

Posts a canonical `{"title", "body", "type", "format"}` envelope to
`{BASE_URL}@<channel>` with Bearer auth.  The gateway transformer converts it
into the upstream-native payload and forwards it.

## Parameters

- `channel` — the transformer channel selector appended to the base URL as
  `@<channel>` (default `gateway`).

## Versions

### v1 — initial release

- POST the canonical envelope to `{BASE_URL}@<channel>` with Bearer auth;
  print `sent (HTTP <status>)`.
