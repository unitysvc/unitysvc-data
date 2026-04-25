+++
preset_name = "uptime_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of an uptime-monitoring bridge service"
is_active = true
is_public = true
+++

# uptime / description — uptime bridge service description

Markdown overview for uptime-monitoring bridge services routed
through the UnitySVC gateway. Shows the curl one-liner for an
on-demand check and documents the response shape so customers can
plug the bridge into their own dashboards or CI.

## Template tokens — **not** Jinja2

`{{ SERVICE_BASE_URL }}` and `{{ API_KEY }}` are **literal**
placeholders shown to customers. The file is `description.md`,
not `description.md.j2`, so SDK rendering leaves them intact.

## Versions

### v1 — initial release

- Curl quickstart with empty `{}` body (the bridge fills in check
  parameters from the enrollment).
- Documented response shape: `status` + `metrics.response_ms`.
