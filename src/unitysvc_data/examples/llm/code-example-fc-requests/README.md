+++
preset_name = "llm_code_example_fc_requests"
category = "code_example"
mime_type = "python"
file = "code-example-fc.py"
description = "Python example: chat completion with function/tool calling on an OpenAI-compatible LLM"
is_active = true
is_public = true
meta = { requirements = ["requests"] }
+++

# llm / code-example-fc-requests — chat completion with function calling via `requests`

Customer-facing Python example showing the modern OpenAI-style
`tools` + `tool_choice` payload (not the deprecated `functions`
parameter). The script declares a single tool, sends a prompt that
should trigger it, and dispatches the model's `tool_calls` back to
the local `echo_message` implementation.

## Environment variables (all required)

- `SERVICE_BASE_URL` — chat-completion endpoint.
- `UNITYSVC_API_KEY` — bearer token.
- `MODEL` — interface-specific model identifier. The script does not
  fall back to `offering.name` because the model id is a routing
  key and can differ between the gateway and the upstream — the
  caller must supply the correct one for the access interface.

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
- Plain Python (no `.j2` suffix) — no Jinja2 expansion.
