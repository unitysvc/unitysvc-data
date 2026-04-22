+++
preset_name = "s3_connectivity"
category = "connectivity_test"
mime_type = "python"
file = "connectivity.py.j2"
description = "Verify S3 endpoint accepts the configured credentials"
is_active = true
is_public = false
meta = { output_contains = "connectivity ok", requirements = ["boto3"] }
+++

# s3 / connectivity — S3 credential smoke test

Python smoke test that proves **credentials are accepted** by the S3
endpoint. It does not try to access a specific bucket — the point is
"can the user authenticate against the upstream", not "does bucket X
exist" — so AccessDenied on a list call still counts as pass.

## Branches (rendered at upload time with the listing context)

| `local_testing` | `interface.access_key` | Behaviour |
|-----------------|------------------------|-----------|
| `true`          | present                | Signs with seller credentials and calls `list_buckets()`. |
| `true`          | absent                 | Public bucket — prints `connectivity ok` and exits 0 without network call. |
| `false`         | —                      | Signs with the customer's `UNITYSVC_API_KEY` via the gateway and calls `list_objects_v2(Bucket=..., MaxKeys=1)` against the gateway-resolved bucket. |

## Environment variables (local mode)

- `REGION`, `ACCESS_KEY`, `SECRET_KEY` — seller credentials.
- `S3_ENDPOINT` — optional; set for non-AWS endpoints (DigitalOcean
  Spaces, MinIO, etc.).

## Environment variables (gateway mode)

- `SERVICE_BASE_URL` — form: `{endpoint_prefix}/{service_slug}`. The
  script splits on the last `/` to recover `endpoint_url` and `bucket`.
- `UNITYSVC_API_KEY` — customer's gateway key, used as
  `aws_access_key_id`; `aws_secret_access_key` is set to `"not-used"`
  because the gateway ignores it.

## Auth-failure classification

Only these error codes are treated as genuine auth rejection:
`InvalidAccessKeyId`, `SignatureDoesNotMatch`, `InvalidClientTokenId`,
and any HTTP 401. Anything else (including 403 AccessDenied) means the
signature was accepted — that's still connectivity ok.

## Versions

### v1 — initial release

- Three-way branch on `local_testing` / `interface.access_key`.
- Treats non-auth `ClientError` as pass.
