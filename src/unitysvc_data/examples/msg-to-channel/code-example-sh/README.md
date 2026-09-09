+++
preset_name = "msg_to_channel_code_example_sh"
category = "code_example"
mime_type = "bash"
file = "code-example.sh.j2"
description = "cURL code example for gateway-transformer notification services"
is_active = true
is_public = true
meta = { output_contains = "sent", min_expected_metrics = { bytes_out = 1 } }
parameters = { channel = "gateway", native_body = "{}", local_url = "" }
+++

# msg-to-channel / code-example-sh

cURL code example for gateway *transformer* channels — channels that transform a
canonical message envelope `{title, body, type, format}` into the upstream
provider's native payload **inside the gateway** and POST it directly upstream,
bypassing Apprise. A plain `curl` request is easier to read and copy-paste than
the Python/httpx equivalent (`msg_to_channel_code_example_py`), which documents
the same request shapes.

The transformer channel is selected at request time via an `@<channel>` selector
on the service base URL (e.g. `@gateway`, `@gateway-plus`). The gateway applies
that selector to `BASE_URL` server-side, so this example POSTs to the bare
`{{ service_base_url }}` and does **not** append `@<channel>` itself.

## Local mode

`local_testing` is true. POSTs the channel-NATIVE body (`native_body`) straight
to a mock upstream (`local_url`) with `Content-Type: application/json` (or the
upstream's native content type — form-encoded or XML for a handful of
channels) and no platform auth — there is no gateway in the loop to compose the
payload or attach credentials. Any HTTP 2xx is treated as success.

## Gateway mode

`local_testing` is false. Posts a canonical `{"title":"t","body":"hi","type":"info","format":"text"}`
envelope to `{{ service_base_url }}` with a `Bearer $UNITYSVC_API_KEY` header.
The gateway transformer converts it into the upstream-native payload and
forwards it.

## Parameters

- `channel` — the transformer channel selector (default `gateway`). Retained for
  compatibility; the gateway applies the `@<channel>` selector to `BASE_URL`
  server-side, so the example no longer appends it.
- `native_body` — the channel-native request body POSTed to `local_url` in local
  mode (e.g. a Discord webhook payload). Used by the generic base preset; the
  channel-specific variants bake the native body in instead.
- `local_url` — the mock upstream URL POSTed to in local mode.

## Variants

Same one-variant-per-channel scheme as `msg_to_channel_code_example_py`: each
variant bakes in that channel's native body, so the caller only supplies the
`channel` selector and the `local_url` mock upstream (no `native_body`). Each
variant becomes its own preset `msg_to_channel_code_example_sh_<channel>`
(hyphens in the channel slug become underscores, e.g. `twilio-sms` →
`msg_to_channel_code_example_sh_twilio_sms`).

Gateway mode is identical across every variant and to the base: POST the
canonical envelope to `{{ service_base_url }}` with Bearer auth. Only the
baked-in local-mode native body (and, for a handful of channels, the request
content type) differs. Most channels POST JSON; `twilio-sms`, `mailgun-email`,
and a dozen others POST form-encoded (`application/x-www-form-urlencoded`)
bodies matching the upstream's native API; `xml-webhook` POSTs raw XML.

Channels with a per-channel variant:

- Chat / team messaging: `slack`, `feishu-msg`, `json`, `ntfy`, `gotify`,
  `discord`, `telegram`, `matrix`, `msteams`, `wechat-work`, `dingtalk`,
  `line-msg`, `whatsapp-msg`, `groupme-msg`, `viber`, `zulip`, `flock`, `ryver`,
  `zoom`, `chime`, `mastodon`, `misskey`, `humhub`, `nextcloud`,
  `nextcloudtalk`, `synologychat`, `matrix-note-placeholder`
- SMS APIs: `twilio-sms`, `vonage-sms`, `plivo-sms`, `sinch-sms`,
  `messagebird-sms`, `clicksend-sms`, `bulksms-sms`, `bulkvs-sms`,
  `burstsms-sms`, `africastalking-sms`, `d7networks-sms`, `elks-sms`,
  `exotel-sms`, `httpsms-sms`, `seven-sms`, `octopush-sms`, `msg91-sms`,
  `smseagle-sms`
- Email APIs: `notificationapi`, `brevo-email`, `sendgrid-email`,
  `mailgun-email`, `postmark-email`, `resend-email`, `smtp2go-email`,
  `sparkpost-email`, `popcornnotify`
- Push services: `bark`, `fcm`, `pushy`, `onesignal`, `kumulos`,
  `parseplatform`, `pushbullet`, `pushover`, `pushjet`, `pushed`, `pushplus`,
  `pushdeer`, `pushsafer`, `prowl`, `simplepush`, `techulus`, `spikesh`,
  `spugpush`, `serverchan`, `chanify`, `qqpush`, `wxpusher`, `freemobile`,
  `notica`, `streamlabs`, `lametric`, `dot`, `kodi`, `homeassistant`, `dapnet`
- Ops / incident / webhooks: `ifttt`, `notifiarr`, `opsgenie`, `pagerduty`,
  `pagertree`, `victorops`, `signl4`, `jira`, `signl4-placeholder`,
  `form-webhook`, `xml-webhook`

## Versions

### v1 — initial release

- Local: `curl -X POST` the channel-NATIVE body (base preset: `native_body`
  parameter; variants: baked in) to `local_url`; treat any HTTP 2xx as success.
- Gateway: `curl -X POST` the canonical envelope to `{{ service_base_url }}`
  with Bearer auth; treat any HTTP 2xx as success. Mirrors
  `msg_to_channel_code_example_py` request-for-request — same bodies, same
  headers, same success criteria — just written as a `curl` one-liner instead
  of a Python script.
