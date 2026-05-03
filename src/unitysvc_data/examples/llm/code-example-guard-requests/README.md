+++
preset_name = "llm_code_example_guard_requests"
category = "code_example"
mime_type = "python"
file = "code-example-guard.py.j2"
description = "Python example: probe a Llama-Guard-style safety classifier with a borderline prompt"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-guard-requests — safety classifier probe via `requests`

Customer-facing Python example for safety classifiers exposed
through the OpenAI-compatible chat-completion route (Llama Guard,
HF safety models, etc.). Sends a deliberately unsafe prompt and
prints the model's response so the caller can verify the classifier
flags it.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## Conventions

- The prompt is intentionally an obvious prompt-injection +
  jailbreak attempt — guard models should respond with a refusal /
  classification ("unsafe", policy code, etc.).
- Prints the raw response so the caller sees both the classifier
  verdict and any per-provider envelope.

## Versions

### v1 — initial release

- Chat-completion POST with a single jailbreak-shaped user message.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from env;
  missing any of the three fails fast with `KeyError`.
