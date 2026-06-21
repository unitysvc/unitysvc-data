+++
preset_name = "notify_relay_connectivity"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Connectivity test for pass-through HTTP notification services"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok" }
parameters = { webhook_path = "/webhook", chat_id = "" }
+++

# notification / connectivity

Connectivity test for pass-through notification services. One variant per
upstream API shape; each becomes its own preset (e.g. `notification_connectivity_discord`).

## Local mode

Posts a minimal upstream-format ping directly to the webhook at
`service_base_url + webhook_path`. Asserts the upstream-specific success code.

## Gateway mode

Posts the **same** upstream-format ping to the UnitySVC gateway endpoint.
Only adds `Authorization: Bearer ${UNITYSVC_API_KEY}`. The gateway forwards
the payload to the upstream unchanged.

## Parameters

- `webhook_path` — path appended to `service_base_url` in local mode.
- `chat_id` — receiver ID used by telegram variant.

## Upstream type reference

The relay forwards the customer's **native** upstream body unchanged, so each
distinct upstream body shape is its own variant `notify_relay_<kind>_<channel>`.
Most providers differ, so most channels have a 1:1 variant. A few share an
identical body and reuse one variant:

| Shared variant | Native body | Channels |
|---|---|---|
| `slack` | `{"text":".."}` | slack, googlechat, mattermost, rocketchat, webex |
| `discord` | `{"embeds":[..]}` / `{"content":".."}` | discord, guilded, revolt |
| `feishu-msg` | `{"msg_type":"text","content":{"text":".."}}` | feishu_msg, lark |
| `json` | `{"message":".."}` | json, ntfy (gotify adds `priority`) |

Every other relay-capable channel has its own variant named after the channel
(e.g. `notify_relay_connectivity_twilio_sms`). 60 such variants were added in
v0.1.23, covering the apprise catalog's POST-relayable channels (chat, push,
SMS/email APIs, generic webhooks).

**Not relay-capable** — no relay preset; use the channel's `msg-to-<channel>`
apprise service instead. A relay needs ONE credential-injectable HTTP POST that
carries the message in its body, which these can't provide:
- OAuth2 / token-exchange at send time: office365_email, reddit, sendpulse_email, ringcentral_sms, wechat
- OAuth1 signing: twitter — AWS SigV4 signing: ses_email, sns
- Multi-step login: bluesky, emby, jellyfin, twist
- Per-request signing/encryption: session, vapid — Non-HTTP (SMTP): smtp_email
- Message rides in the URL query, no body to relay: threema, sfr_sms, voipms_sms, smsmanager_sms, clickatell_sms, kavenegar_sms, join, notifico, pushme, enigma2

## Versions

### v1 — initial release

- Local: POST upstream-format ping; assert upstream-specific success code.
- Gateway: POST same ping with Bearer auth; assert HTTP 2xx.
