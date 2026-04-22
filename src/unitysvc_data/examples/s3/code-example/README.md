+++
preset_name = "s3_code_example"
category = "usage_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: list objects in an S3 bucket via boto3"
is_active = true
is_public = true
+++

# s3 / code-example — list objects via boto3

Customer-facing primary example for S3 gateway services. Lists up to
five objects from the bucket using `boto3` and prints their keys.

## Branches (rendered at upload time with the listing context)

| `local_testing` | `interface.access_key` | Behaviour |
|-----------------|------------------------|-----------|
| `true`          | present                | Uses seller credentials + optional `S3_ENDPOINT`. |
| `true`          | absent                 | Unsigned `boto3` client against a public bucket. |
| `false`         | —                      | Gateway-routed with the customer's `UNITYSVC_API_KEY`. |

## Environment variables (local mode)

- `REGION`, `ACCESS_KEY`, `SECRET_KEY` — seller credentials (only when
  `interface.access_key` is set).
- `S3_ENDPOINT` — optional, for non-AWS S3.
- `BUCKET` — bucket to list.
- `BASE_PATH` — optional prefix; stripped from printed keys.

## Environment variables (gateway mode)

- `SERVICE_BASE_URL` — split on `/` to extract `endpoint_url` and
  `bucket`.
- `UNITYSVC_API_KEY` — used as `aws_access_key_id`.

## Conventions

- Ends with `print("connectivity ok")` so the same script is usable as
  a smoke test if a seller wants to reuse it.
- Prints `<key>  (<size> bytes)` per object, up to five.

## Versions

### v1 — initial release

- Three-branch (seller creds / unsigned / gateway) rendering based on
  `local_testing` and `interface.access_key`.
