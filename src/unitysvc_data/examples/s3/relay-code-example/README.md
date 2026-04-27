+++
preset_name = "s3_relay_code_example"
category = "code_example"
mime_type = "python"
file = "relay-code-example.py.j2"
description = "Python example: list and download objects via an S3 relay (BYOE bucket)"
is_active = true
is_public = true
meta = { output_contains = "connectivity ok", requirements = ["boto3"] }
+++

# s3 / relay-code-example — S3 relay Python example

Customer-facing primary example for S3 relay services (BYOE bucket
patterns). Uses boto3 to list objects in the relay bucket, supporting
both authenticated seller credentials in local-test mode and the
gateway API key in customer-facing mode.

## Branches

| `local_testing` | `access_key` present | Behaviour |
|-----------------|---------------------|-----------|
| `true`          | yes                 | Signs requests with `ACCESS_KEY`/`SECRET_KEY` using the `S3_ENDPOINT`. |
| `true`          | no                  | Uses unsigned client against the endpoint. |
| `false`         | —                   | Gateway-routed with the customer's `UNITYSVC_API_KEY`. |

## Environment variables (local mode)

- `S3_ENDPOINT` — S3-compatible endpoint URL; falls back to `SERVICE_BASE_URL`.
- `BUCKET` — bucket name to list.
- `REGION` — region (e.g. `us-east-1`).
- `ACCESS_KEY`, `SECRET_KEY` — seller credentials (when present in upstream config).

## Environment variables (gateway mode)

- `SERVICE_BASE_URL` — gateway URL, optionally with a path segment that
  identifies the bucket or routing key (e.g. `https://gw/bucket`). When
  the URL has no path (multi-enrollment services), the probe is skipped.
- `UNITYSVC_API_KEY` — used as `aws_access_key_id`.

## Conventions

- Ends with `print("connectivity ok")` so the example also functions
  as a smoke test.

## Versions

### v1 — initial release

- Three-branch rendering on `local_testing` / `access_key`.
- 403 AccessDenied is treated as "credentials accepted, list not permitted".

### v2 — urlparse; skip multi-enrollment probe

- Replaces `rsplit('/', 1)` with `urlparse` so the endpoint URL is
  always valid (v1 produced `https:/` when `SERVICE_BASE_URL` had no
  path component).
- When the parsed path has no segments (multi-enrollment services whose
  `SERVICE_BASE_URL` is just the gateway host), the S3 probe is skipped
  and the script exits with `connectivity ok`.
