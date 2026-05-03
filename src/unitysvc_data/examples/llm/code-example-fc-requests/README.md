+++
preset_name = "llm_code_example_fc_requests"
category = "code_example"
mime_type = "python"
file = "code-example-fc.py.j2"
description = "Python example: chat completion with function/tool calling on an OpenAI-compatible LLM"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
parameters = { version_prefix = "/v1" }
+++

# llm / code-example-fc-requests — chat completion with function calling via `requests`

Customer-facing Python example showing the modern OpenAI-style
`tools` + `tool_choice` payload (not the deprecated `functions`
parameter). The script declares a single tool, sends a prompt that
should trigger it, and dispatches the model's `tool_calls` back to
the local `echo_message` implementation.

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, taken from the listing's access interface.
- `{{ routing_key.model }}` — model id, taken from the access interface's routing key.

## Environment variables (read at runtime)

Required:

- `UNITYSVC_API_KEY` — bearer token: customer's svcpass for gateway access, or an upstream API key when the seller / customer wires it as a secret (BYOK).

## What this exercises

- The model accepts a `tools` array and emits `tool_calls` instead of
  inline content when the prompt is tool-shaped.
- `tool_call.function.arguments` arrives as a JSON-encoded string and
  must be `json.loads`-ed before use.
- Falls back to printing `message.content` when the model declines to
  call the tool, so the script always produces output.

## Single-turn vs multi-turn

This example is **single-turn**: it surfaces the tool call but does
not feed the result back into the conversation. Multi-turn handling
(sending the tool's output back as a `tool` role message and asking
the model for a final answer) is out of scope here — keep it simple
so it's a generic template that providers without strict OpenAI
parity can still pass.

## Versions

### v1 — initial release

- Modern `tools` / `tool_choice: "auto"` payload.
- Reads `UNITYSVC_API_KEY`, `SERVICE_BASE_URL`, `MODEL` from env;
  missing any of the three fails fast with `KeyError`.
- Single `echo_message` tool wired to a local function.
