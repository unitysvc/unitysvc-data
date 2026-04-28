+++
preset_name = "llm_code_example_openai_javascript"
category = "code_example"
mime_type = "javascript"
file = "code-example.js.j2"
description = "JavaScript example: send a chat completion request to an OpenAI-compatible LLM using the openai SDK"
is_active = true
is_public = true
meta = { requirements = ["openai"] }
+++

# llm / code-example-openai-javascript — chat completion via the `openai` Node.js SDK

Customer-facing Node.js example for OpenAI-compatible chat
completion services using the official `openai` npm package.
Pointing the SDK at `SERVICE_BASE_URL` works against any LLM
gateway preset since they all expose an OpenAI-compatible
chat-completion route.

The companion preset `llm_code_example_javascript` shows the same
call using the built-in `fetch` API, for callers who don't want
to add the `openai` dependency.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint, passed as
  `baseURL`.
- `UNITYSVC_API_KEY` — passed as `apiKey`.
- `MODEL` — interface-specific model identifier.

## Versions

### v1 — initial release

- CommonJS `require("openai")` so the file runs as plain
  `node code-example.js` without ESM/`type:"module"` setup.
- HTTP errors surface as `OpenAIError` subclasses; `main().catch`
  exits 1 with a clean message.
