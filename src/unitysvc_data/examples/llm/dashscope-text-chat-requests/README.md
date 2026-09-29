+++
preset_name = "llm_code_example_chat_dashscope_text_requests"
category = "code_example"
mime_type = "python"
file = "code-example.py.j2"
description = "Python example: send a chat completion to a DashScope text-generation endpoint using the requests library"
is_active = true
is_public = true
meta = { variant = "Chat (DashScope text)", requirements = ["requests"], min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "chat", dialect = "dashscope_text", upstream = "dashscope" }
+++

# llm / dashscope-text-chat-requests

DashScope serves a TEXT-ONLY model at `aigc/text-generation/generation`,
where `input.messages[].content` is a **string** and the reply carries
`output.choices[].message.content` as a **string**. Its multimodal sibling
(`aigc/multimodal-generation/generation`) takes and returns an **array of
parts**, and the two are not interchangeable: posting either shape to the other
path answers `HTTP 400 InvalidParameter: url error, please check url`. Verified
in both directions against the live API.

That is why the dialect token is `dashscope_text` rather than plain `dashscope` —
the endpoint, the request shape and the response shape all move together, so they
are one wire dialect, and a service must say which of the two it speaks. Neither
is the default; a group naming a bare `dashscope` selects neither, which fails
where it can be seen rather than sending the wrong shape.

The request pins `parameters.result_format` to `"message"`. Text-generation
returns whichever shape the MODEL defaults to otherwise — `output.text` for some,
`output.choices[].message` for others — and a reader cannot be written against
both. Pinning it makes the response shape a property of the request.

Assertions check the payload rather than the status, because DashScope answers
**200 with an error envelope**. They sit behind `{%- if not customer_display %}`
so the published example stays clean.

## Versions

### v1 — initial release

- POST `model` + `input.messages` with `content` as a string.
- No vendor SDK; `requests` only.
- Raises with the response body on a non-2xx, rather than `raise_for_status`,
  which discards it.
- **Amended in 0.2.5**: `parameters.result_format` is now pinned to `"message"`.
  Without it DashScope's text-generation returns whichever shape the MODEL
  defaults to — `output.text` for some, `output.choices[].message` for others —
  so an example that reads `choices` failed on half the catalog with
  `Cannot read properties of undefined`. Probed both ways on `qwen-flash`:
  absent gives `{"output":{"text":…}}`, `"message"` gives
  `{"output":{"choices":[…]}}`. The reader is unchanged; the request now asks for
  the shape it reads.
