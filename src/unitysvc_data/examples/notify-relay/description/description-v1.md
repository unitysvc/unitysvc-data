## Push Notifications via UnitySVC

Publish push notifications through the UnitySVC notification
gateway. The endpoint speaks the ntfy protocol: the message body is
the notification text, and metadata (title, priority, tags) is
carried in HTTP headers.

```bash
curl -X POST "{{ SERVICE_BASE_URL }}" \
  -H "Authorization: Bearer {{ API_KEY }}" \
  -H "Title: Build finished" \
  -H "Priority: default" \
  -H "Tags: white_check_mark" \
  -d "Deploy to staging completed in 2m 14s"
```

The gateway authenticates you, resolves the upstream topic from
your enrollment, and forwards the publish. Subscribers see the
message immediately on any ntfy-compatible client (web, iOS,
Android, CLI).
