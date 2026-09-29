+++
preset_name = "llm_connectivity_chat_dashscope_text"
category = "connectivity_test"
mime_type = "bash"
file = "connectivity.sh.j2"
description = "Verify a DashScope text-generation endpoint by issuing a tiny request (chat)"
is_active = true
is_public = false
meta = { min_expected_metrics = { input_tokens = 1, output_tokens = 1 } }
applies_to = { capability = "chat", dialect = "dashscope_text", upstream = "dashscope" }
+++

# llm / dashscope-text-chat-connectivity

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

Assertions check the payload rather than the status, because DashScope answers
**200 with an error envelope**. They sit behind `{%- if not customer_display %}`
so the published example stays clean.

## Versions

### v1 — initial release

- The smallest useful request the text-generation endpoint takes.
- Asserts the reply carries `"choices"`; a 2xx alone is not enough.
