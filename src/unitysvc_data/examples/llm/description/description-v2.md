## Using LLM services on UnitySVC

Every LLM service here is reached through the [API Gateway](?topic=api-gateway) —
one base URL, one `svcpass_…` [API key](?topic=api-key). The gateway
authenticates you, selects the upstream, translates the request format when
needed, and meters usage. This page's pricing, channels, and code examples are
specific to this service; everything below applies to LLM services
platform-wide.

### Channels — who supplies the upstream credential

A [channel](?topic=channel) decides who pays the provider:

- **managed** — call it directly, nothing to configure. Billed to your
  UnitySVC [wallet](?topic=wallet) at the seller-determined
  [price](?topic=pricing) shown on this page.
- **byok** — bring your own provider key, stored as a customer
  [secret](?topic=secret). You pay the upstream provider directly.
- **byoe** — point the service at your own endpoint. Uncommon; for
  self-hosted upstreams.

With no selector the gateway picks the highest-ranked channel your call can
satisfy. Pin one by appending `@managed` or `@byok` to the service path. See
[Listing Types](?topic=listing-types) for how a seller publishes each kind, and
[Enrollment](?topic=enrollment) for channels that bind your own credential.

### Trying it

The code examples on this page are rendered with this service's real base URL
and model name — they run as-is once you export your API key. Signed in, the
**Test Request** panel calls the model straight from the browser.

### Request formats

Most LLM services accept more than one wire format. [OpenAI](?topic=openai-format)
and [Anthropic](?topic=anthropic-format) are the common pair, and some also
expose a provider-native one — [Converse](?topic=converse-format) for Amazon
Bedrock. The gateway detects the dialect and translates, so you can call in
whichever style your client already speaks. This service's accepted formats are
listed above; see [Input & Output Formats](?topic=input-formats) for how they
are declared.

### Beyond a single service

Any LLM service composes with [request primitives](?topic=request-primitives) —
URL prefixes, no SDK required:

- [Service groups](?topic=service-group) `/g/` and
  [capability pools](?topic=capability-pool) `/p/` spread calls across
  equivalent services from different providers.
- An [alias](?topic=alias) `/a/` gives you a stable URL you can re-point without
  touching code — this is how you point [Claude Code](?topic=claude-code) at the
  platform.
- [Log](?topic=log) `/l/` forces per-call request logging;
  [memoize](?topic=memoize) `/m/` caches responses for a TTL, and cache hits
  aren't billed.

Prefixes stack, so one URL can combine them:

```text
POST /m/l/a/llm/chat/completions
```
