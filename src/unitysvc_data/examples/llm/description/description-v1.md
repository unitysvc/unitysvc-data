## OpenAI-compatible LLM via UnitySVC

Send chat-completion, embedding, and audio requests through the
UnitySVC LLM gateway with any OpenAI-compatible client. Authenticate
once with your UnitySVC API key; the gateway resolves the upstream
provider from your enrollment and proxies the request.

```python
from openai import OpenAI

client = OpenAI(
    base_url="{{ SERVICE_BASE_URL }}",
    api_key="{{ API_KEY }}",
)

response = client.chat.completions.create(
    model="{{ MODEL }}",
    messages=[
        {"role": "user", "content": "Hello!"},
    ],
)
print(response.choices[0].message.content)
```

The same gateway URL and key work with the `openai` Node.js SDK, raw
`requests`/`fetch`, or `curl` — pick whichever fits your stack.

## Streaming

Streaming responses are supported on chat-completion endpoints whose
upstream advertises SSE. Pass `stream=True` (or `stream: true` in JS)
and iterate the returned generator.
