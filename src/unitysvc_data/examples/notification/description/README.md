+++
preset_name = "notification_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of a ntfy-shaped push-notification gateway service"
is_active = true
is_public = true
+++

# notification / description — notification gateway service description

Markdown overview for push-notification services that speak the
ntfy publish protocol routed through the UnitySVC gateway. Shows
the curl one-liner that's enough to send a notification.

## Template tokens — **not** Jinja2

`{{ SERVICE_BASE_URL }}` and `{{ API_KEY }}` are **literal**
placeholders shown to customers. The file is `description.md`,
not `description.md.j2`, so SDK rendering leaves them intact.

## Versions

### v1 — initial release

- Curl quickstart with `Title` / `Priority` / `Tags` metadata
  headers.
- Closing paragraph framing the publish-and-fanout flow.
