+++
preset_name = "recommender_description"
category = "getting_started"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of a Gorse-shaped recommender gateway service"
is_active = true
is_public = true
+++

# recommender / description — recommender gateway service description

Markdown overview for Gorse-shaped recommendation services routed
through the UnitySVC gateway. Shows the two-step usage pattern
(submit feedback, fetch recommendations) so customers can get
started without reading the upstream docs.

## Template tokens — **not** Jinja2

`{{ SERVICE_BASE_URL }}`, `{{ API_KEY }}`, and `{{ USER_ID }}` are
**literal** placeholders shown to customers. The file is
`description.md`, not `description.md.j2`, so SDK rendering leaves
them intact.

## Versions

### v1 — initial release

- Two-step quickstart (POST `/api/feedback`, GET
  `/api/recommend/<user>`).
- One-paragraph framing of how the gateway proxies to upstream
  Gorse.
