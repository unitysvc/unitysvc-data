import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ["SERVICE_BASE_URL"],
    api_key=os.environ["UNITYSVC_API_KEY"],
)

stream = client.chat.completions.create(
    model=os.environ["MODEL"],
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say this is a test"},
    ],
    stream=True,
)

for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()
