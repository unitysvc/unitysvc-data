+++
preset_name = "llm_code_example_anthropic_fc"
category = "code_example"
mime_type = "python"
file = "code-example-anthropic-fc.py.j2"
description = "Python example: tool use against an Anthropic Messages API endpoint via the anthropic SDK"
is_active = true
is_public = true
meta = { requirements = ["anthropic"] }
+++

# llm / code-example-anthropic-fc — Anthropic tool use via the `anthropic` SDK

Customer-facing Python example demonstrating tool use ("function
calling") against the Anthropic Messages API.

The Anthropic tools API differs from OpenAI's:

- Tool definitions use `input_schema`, not nested `function.parameters`.
- Tool **calls** appear as `content` blocks of `type: "tool_use"`,
  not as a separate `tool_calls` field.
- Tool **results** are sent back as content blocks of
  `type: "tool_result"` in a follow-up `user` message — Anthropic
  doesn't have a `role: "tool"` message type.

So tool-use examples need their own preset rather than reusing
`llm_code_example_fc_requests` (which is OpenAI-shaped and would 4xx
against `/v1/messages`).

## Template variables (filled in by the platform when rendering for a given access interface)

- `{{ service_base_url }}` — endpoint base URL, passed to
  `Anthropic(base_url=...)`.
- `{{ routing_key.model }}` — model id.

## Environment variables (read at runtime)

- `UNITYSVC_API_KEY` — required. Bearer token: customer's svcpass for
  gateway access, or an upstream Anthropic key when wired as a secret
  (BYOK).

## Versions

### v1 — initial release

- Defines a single `echo_message(message)` tool, asks the model to
  echo a phrase, then walks the response `content` blocks looking for
  `tool_use` items.
- Prints the tool result if the model invoked the tool, otherwise
  prints whatever text content came back.
- HTTP errors surface as `anthropic.APIStatusError` (non-zero exit).
