+++
preset_name = "llm_code_example_guard_python"
category = "code_example"
mime_type = "python"
file = "code-example-guard.py.j2"
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

## Environment variables

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — optional; defaults to `offering.name`.

## Conventions

- The prompt is intentionally an obvious prompt-injection +
  jailbreak attempt — guard models should respond with a refusal /
  classification ("unsafe", policy code, etc.).
- Prints the raw response so the caller sees both the classifier
  verdict and any per-provider envelope.

## Versions

### v1 — initial release

- Chat-completion POST with a single jailbreak-shaped user message.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from env.
