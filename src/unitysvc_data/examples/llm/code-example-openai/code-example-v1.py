import os

from openai import OpenAI

client = OpenAI(
    base_url=os.environ["SERVICE_BASE_URL"],
    api_key=os.environ["UNITYSVC_API_KEY"],
)

response = client.chat.completions.create(
    model=os.environ["MODEL"],
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say this is a test"},
    ],
)
print(response.choices[0].message.content)
