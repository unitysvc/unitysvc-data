+++
preset_name = "notification_code_example_python"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: publish a push notification through a ntfy-shaped notification gateway"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# notification / code-example-python — ntfy publish

Customer-facing Python example for ntfy-shaped notification
services. ntfy carries the message metadata (title, priority, tags)
in HTTP headers and the message body as the request body, which is
why the call uses `data=` rather than `json=`.

## Environment variables

- `SERVICE_BASE_URL` — full publish URL, including the topic. Set by
  the gateway after enrollment.
- `UNITYSVC_API_KEY` — bearer token.

## Conventions

- Sends a `Title`, `Priority`, and `Tags` header so the resulting
  notification is recognisable in client UIs.
- Prints the parsed JSON response (ntfy returns the published
  message envelope).

## Versions

### v1 — initial release

- POST text body to `SERVICE_BASE_URL` with metadata headers.
- `raise_for_status()` so non-2xx exits with a traceback.
