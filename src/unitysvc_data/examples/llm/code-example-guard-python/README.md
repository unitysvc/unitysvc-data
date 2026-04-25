+++
preset_name = "llm_code_example_guard_python"
category = "code_example"
mime_type = "python"
file = "code-example-guard.py"
description = "Python example: probe a Llama-Guard-style safety classifier with a borderline prompt"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-guard-python — safety classifier probe

Customer-facing Python example for safety classifiers exposed
through the OpenAI-compatible chat-completion route (Llama Guard,
HF safety models, etc.). Sends a deliberately unsafe prompt and
prints the model's response so the caller can verify the classifier
flags it.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

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
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
