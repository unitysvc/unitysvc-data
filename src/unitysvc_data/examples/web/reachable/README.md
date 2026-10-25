+++
preset_name = "website_reachable"
category = "connectivity_test"
mime_type = "bash"
file = "reachable.sh.j2"
description = "Verify the seller's website is reachable"
is_active = true
is_public = true
+++

# web / reachable — website reachability test

Connectivity test for an **external** channel (`"type": "external"`): a
service the customer uses at the seller's own website or app rather than
through a UnitySVC gateway (unitysvc/unitysvc#2709). The platform cannot
call such a service, so the evidence that it is still alive is that its
website answers. This test runs at submission and in the daily health
sweep; a site that stays unreachable gets the service unlisted.

Scope it to the external channel with `meta.channels` when the service has
other channels:

```json
"Website": {"$doc_preset": {"name": "website_reachable", "meta": {"channels": ["website"]}}}
```

## Pass / fail classification

Redirects are followed (up to 5), and the **final** response decides.

| Final HTTP status | Verdict | Rationale |
|-------------------|---------|-----------|
| 2xx               | pass    | the site serves a page |
| 401, 403          | fail    | a public homepage should not require credentials |
| 404               | fail    | the URL no longer exists |
| 5xx               | fail    | the site is broken |
| 000               | fail    | connect / DNS / TLS / timeout |

Unlike `api_connectivity`, 401/403 are failures: that preset tests API
endpoints, where an auth challenge proves the endpoint is alive; a homepage
answering one usually means the site moved behind a login or is gone.

## Template variables

- `{{ service_base_url }}` — the external channel's `base_url` (the website).

## Environment variables

None. No credential is ever sent to the seller's website.

## Versions

### v1 — initial release

- Follows up to 5 redirects; passes only on a final 2xx.
- Timeout: 10 seconds.
- Works under `set -o pipefail` on bash 3.2 (macOS default).
