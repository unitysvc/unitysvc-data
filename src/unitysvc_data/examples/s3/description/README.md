+++
preset_name = "s3_description"
category = "description"
mime_type = "markdown"
file = "description.md"
description = "Customer-facing overview of the S3 gateway service"
is_active = true
is_public = true
+++

# s3 / description — S3 gateway service description

Markdown overview shown to customers on the listing page. Gives them a
short narrative about the gateway plus a minimal `boto3` snippet they
can copy-paste.

## What's in the description

- One-sentence framing of the gateway.
- A `boto3.client('s3', ...)` snippet with the four fields a customer
  needs to fill in: `endpoint_url`, `aws_access_key_id`,
  `aws_secret_access_key` (always `"not-used"` for this gateway), and
  the `Bucket` for the `list_objects_v2` call.
- Closing paragraph explaining how the gateway authenticates, resolves
  the upstream bucket, and proxies the request.

## Template tokens — **not** Jinja2

The description file contains `{{ S3_GATEWAY_PUBLIC_URL }}`,
`{{ API_KEY }}`, and `{{ SERVICE_NAME }}` tokens. These are deliberately
**not** rendered by the SDK — the file's name is `description.md`, not
`description.md.j2`, so Pass-2 rendering leaves the tokens intact.
Customers see them as literal placeholders they're expected to replace
with their own values.

If a future variant wants server-rendered tokens, add it as a new
`[[versions]]` entry with a `description-v2.md.j2` file alongside the
existing `description-v1.md` — do not convert `_v1` in place.

## Versions

### v1 — initial release

- Static markdown; `{{ ... }}` tokens are literal placeholders shown
  to customers.
