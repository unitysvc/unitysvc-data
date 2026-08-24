+++
preset_name = "llm_code_example_bedrock_invoke"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: call the model with boto3 invoke_model() pointed at the UnitySVC gateway — same endpoint and SigV4 authentication as Converse, but the request body is the provider's NATIVE format"
is_active = true
is_public = true
meta = { variant = "boto3 InvokeModel", requirements = ["boto3"], test = { status = "skip" } }
applies_to = { capability = "chat", dialect = "bedrock_invoke", upstream = "openai" }
+++

# llm / code-example-bedrock-invoke — native Bedrock runtime InvokeModel via boto3

`invoke_model()` counterpart of `code-example-bedrock-converse`: **same
endpoint** (`…/model/<modelId>`), same SigV4-via-gateway authentication —
only the request body differs. InvokeModel carries the **provider's native
format**, not the unified Converse schema; the body in the example is the
Anthropic Messages shape used by `anthropic.*` model ids, with a note to
adjust it per model family. `invoke_model_with_response_stream()` works the
same way.

Ships with `meta.test.status = "skip"` by default: the body is
model-family-specific, so a generic execution against an arbitrary model
would fail for reasons that say nothing about the service. Sellers whose
catalog is a single family can override the meta (and the body via a local
copy) to make it executable.

## Intended scoping (set in the seller's listing, not here)

Like the Converse example, scope it to the native-runtime interface and
SigV4 channel:

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
  gateway (unitysvc/unitysvc#1786).
