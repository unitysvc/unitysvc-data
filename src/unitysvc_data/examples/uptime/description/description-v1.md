## Uptime Monitoring via UnitySVC

On-demand uptime checks routed through the UnitySVC uptime bridge.
The check parameters (target URL, method, accepted status codes,
timeout) are configured once in your enrollment; each request
triggers a fresh probe and returns the current status plus timing
metrics.

```bash
curl -X POST "{{ SERVICE_BASE_URL }}" \
  -H "Authorization: Bearer {{ API_KEY }}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response shape:

```json
{
  "status": "up",
  "metrics": { "response_ms": 142 }
}
```

`status` is `up` / `down` / `degraded` based on the configured
acceptance rules. Use this endpoint to plug uptime data into your
own dashboards, CI checks, or status-page integrations.
