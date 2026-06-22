+++
preset_name = "msg_to_channel_code_example_py"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python (httpx) code example for gateway-transformer notification services"
is_active = true
is_public = true
meta = { output_contains = "sent", requirements = ["httpx"] }
parameters = { channel = "gateway", native_body = "{}", local_url = "" }
+++

# msg-to-channel / code-example-py

Python (httpx) code example for gateway *transformer* channels — channels that
transform a canonical message envelope `{title, body, type, format}` into the
upstream provider's native payload **inside the gateway** and POST it directly
upstream, bypassing Apprise.

The transformer channel is selected at request time by appending `@<channel>` to
the service base URL (e.g. `@gateway`, `@gateway-plus`).

## Local mode

`local_testing` is true.  POSTs the channel-NATIVE body (`native_body`) straight
to a mock upstream (`local_url`) with `Content-Type: application/json` and no
platform auth — there is no gateway in the loop to compose the payload or attach
credentials.  Any HTTP 2xx is treated as success.

## Gateway mode

`local_testing` is false.  Posts a canonical `{"title", "body", "type",
"format"}` envelope to `{BASE_URL}@<channel>` with Bearer auth.  The gateway
transformer converts it into the upstream-native payload and forwards it.

## Parameters

- `channel` — the transformer channel selector appended to the base URL as
  `@<channel>` in gateway mode (default `gateway`).
- `native_body` — the channel-native request body POSTed to `local_url` in local
  mode (e.g. a Discord webhook payload). Used by the generic base preset; the
  channel-specific variants bake the native body in instead.
- `local_url` — the mock upstream URL POSTed to in local mode.

## Variants

The generic base preset takes the channel-native local-mode body as the
`native_body` parameter — awkward, because the native body differs per upstream
channel. Channel-specific variants instead **bake the native body in**, so the
caller only supplies the `channel` selector and the `local_url` mock upstream
(no `native_body`). Each variant becomes its own preset
`msg_to_channel_code_example_py_<channel>`.

- `discord` (`msg_to_channel_code_example_py_discord`) — local mode POSTs a
  baked-in Discord embed body to `local_url`. Gateway mode is identical to the
  base: POST the canonical envelope to `{BASE_URL}@<channel>` with Bearer auth.

## Versions

### v1 — initial release

- Local: POST `native_body` (base) or the baked-in channel body (variants) to
  `local_url`; assert HTTP 2xx.
- Gateway: POST the canonical envelope to `{BASE_URL}@<channel>` with Bearer
  auth; print `sent (HTTP <status>)`.
