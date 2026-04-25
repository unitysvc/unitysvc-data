import os

from anthropic import Anthropic

client = Anthropic(
    base_url=os.environ["SERVICE_BASE_URL"],
    api_key=os.environ["UNITYSVC_API_KEY"],
)

response = client.messages.create(
    model=os.environ["MODEL"],
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Say this is a test"},
    ],
)
print(response.content[0].text)
