+++
preset_name = "msg_to_channel_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for gateway-transformer notification services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { channel = "gateway", native_body = "{}", local_url = "" }
+++

# msg-to-channel / connectivity

Connectivity test for gateway *transformer* channels — channels that transform a
canonical message envelope `{title, body, type, format}` into the upstream
provider's native payload **inside the gateway** and POST it directly to the
upstream (e.g. discord.com), bypassing Apprise.

Such a channel is selected at request time via an `@<channel>` selector on the
service path (e.g. `@gateway`, `@gateway-plus`). The gateway applies that
selector to `service_base_url` server-side, so these presets POST to the bare
`{{ service_base_url }}` and must **not** append `@<channel>` themselves.

## Local mode

`local_testing` is true.  POSTs the channel-NATIVE body (`native_body`) straight
to a mock upstream (`local_url`).  No platform auth — there is no gateway in the
loop to compose the payload or attach credentials.

## Gateway mode

`local_testing` is false.  POSTs the canonical envelope
`{"title":"connectivity check","body":"ping","type":"info","format":"text"}` to
`{{ service_base_url }}` (the gateway applies the `@<channel>` selector
server-side) with a `Bearer ${UNITYSVC_API_KEY}` header, exercising the full
transformer path.

## Parameters

- `channel` — the transformer channel selector (default `gateway`). Retained for
  compatibility; the gateway applies the `@<channel>` selector to
  `service_base_url` server-side, so the preset no longer appends it.
- `native_body` — the channel-native request body POSTed to `local_url` in local
  mode (e.g. a Discord webhook payload). Used by the generic base preset; the
  channel-specific variants bake the native body in instead.
- `local_url` — the mock upstream URL POSTed to in local mode.

## Variants

The generic base preset takes the channel-native local-mode body as the
`native_body` parameter — awkward, because the native body differs per upstream
channel. There is **one variant per channel**, and each **bakes in that
channel's native body**, so the caller only supplies the `channel` selector and
the `local_url` mock upstream (no `native_body`). Each variant becomes its own
preset `msg_to_channel_connectivity_<channel>` (hyphens in the channel slug
become underscores, e.g. `twilio-sms` → `msg_to_channel_connectivity_twilio_sms`).

Gateway mode is identical across every variant and to the base: POST the
canonical envelope to `{{ service_base_url }}` with Bearer auth. Only the
baked-in local-mode native body differs. For example `discord`
(`msg_to_channel_connectivity_discord`) POSTs a baked-in Discord embed body
(`{"embeds":[{"title":"connectivity check","description":"ping"}]}`) to
`local_url`.

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

- Local: POST `native_body` (base) or the baked-in channel body (variants) to
  `local_url`; assert HTTP 2xx.
- Gateway: POST the canonical envelope to `{{ service_base_url }}` with
  Bearer auth; assert HTTP 2xx.
