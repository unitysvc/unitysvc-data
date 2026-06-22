+++
preset_name = "msg_to_gateway_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for gateway-transformer notification services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { channel = "gateway", native_body = "{}", local_url = "" }
+++

# msg-to-gateway / connectivity

Connectivity test for gateway *transformer* channels — channels that transform a
canonical message envelope `{title, body, type, format}` into the upstream
provider's native payload **inside the gateway** and POST it directly to the
upstream (e.g. discord.com), bypassing Apprise.

Such a channel is selected at request time by appending `@<channel>` to the
service path (e.g. `@gateway`, `@gateway-plus`).

## Local mode

`local_testing` is true.  POSTs the channel-NATIVE body (`native_body`) straight
to a mock upstream (`local_url`).  No platform auth — there is no gateway in the
loop to compose the payload or attach credentials.

## Gateway mode

`local_testing` is false.  POSTs the canonical envelope
`{"title":"connectivity check","body":"ping","type":"info","format":"text"}` to
`{{ service_base_url }}@{{ channel }}` with a `Bearer ${UNITYSVC_API_KEY}` header,
exercising the full transformer path.

## Parameters

- `channel` — the transformer channel selector appended to `service_base_url` as
  `@<channel>` in gateway mode (default `gateway`).
- `native_body` — the channel-native request body POSTed to `local_url` in local
  mode (e.g. a Discord webhook payload).
- `local_url` — the mock upstream URL POSTed to in local mode.

## Versions

### v1 — initial release

- Local: POST `native_body` to `local_url`; assert HTTP 2xx.
- Gateway: POST the canonical envelope to `service_base_url@<channel>` with
  Bearer auth; assert HTTP 2xx.
