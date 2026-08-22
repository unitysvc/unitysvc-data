+++
preset_name = "llm_code_example_bedrock_converse"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: call the model with the native AWS SDK — boto3 converse() pointed at the UnitySVC gateway, which authenticates the svcpass access-key-id and re-signs upstream with the service's stored AWS credentials (SigV4)"
is_active = true
is_public = true
meta = { variant = "boto3 Converse", requirements = ["boto3"], output_contains = "connectivity ok" }
+++

# llm / code-example-bedrock-converse — native Bedrock runtime Converse via boto3

Calls a Bedrock-fronted model with the **native AWS SDK** (`boto3`
`bedrock-runtime` client, `converse()`), pointed at the UnitySVC gateway
instead of AWS. The service URL carries the model id
(`…/model/<modelId>`): everything before `/model/` is the boto3
`endpoint_url`, and the SDK itself appends `/model/<modelId>/converse`.

boto3 signs the request with SigV4 as usual — the customer's UnitySVC API
key rides as the SigV4 **access-key-id** with a documented placeholder
secret. The gateway authenticates the key itself (the signature is not
verified — same trust model as the S3 gateway) and **re-signs** the
finalized request with the service's stored AWS IAM credentials
(`__sigv4__` disposition), so `converse_stream()` and `invoke_model()`
work unchanged.

Driven by the `local_testing` flag:

- **`local_testing`** — call the Bedrock runtime directly; the test runner
  exports the channel's IAM credentials as `AWS_ACCESS_KEY_ID` /
  `AWS_SECRET_ACCESS_KEY` / `AWS_DEFAULT_REGION`, so boto3's default
  credential chain signs with true values.
- **otherwise** — point boto3 at the gateway with the UnitySVC API key as
  the access-key-id and a placeholder secret.

The response parser tolerates **reasoning models**: they emit a
`reasoningContent` block before (or, under a tight `maxTokens`, instead
of) the `text` block, so the example prints the first text block if any,
else the first block as-is — never assuming `content[0]` carries `text`.

## Intended scoping (set in the seller's listing, not here)

This example only makes sense against a **native-runtime access interface**
whose URL carries `/model/<modelId>` and a SigV4 (`__sigv4__`) upstream
channel. Scope it with document meta in the listing, e.g.:

```json
"meta": {"channels": ["converse"], "interfaces": ["converse_api"]}
```

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface (carries `/model/<modelId>`).
- `{{ routing_key.model }}` — fallback model id when the URL carries no `/model/` segment (guarded; optional).
- `{{ region }}` — AWS region for the direct-upstream branch (defaults to `us-east-1`).
- `{{ local_testing }}` — set by the test harness when exercising the upstream directly.

## Environment variables (read at runtime)

Required (gateway branch):

- `UNITYSVC_API_KEY` — the customer's svcpass key, sent as the SigV4 access-key-id.

Required (local-testing branch): AWS IAM credentials via boto3's default
credential chain (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

## Versions

### v1 — initial release
- Extracted from unitysvc-services-bedrock after stabilizing on the live
  gateway (unitysvc/unitysvc#1786): single `"Reply with the single word:
  pong"` user turn, `maxTokens: 64` (headroom for reasoning models),
  reasoning-block-tolerant response parsing, prints `connectivity ok` on
  success.
