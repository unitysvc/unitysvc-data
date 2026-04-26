import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]

response = requests.post(
    SERVICE_BASE_URL,
    headers={
        "Authorization": f"Bearer {UNITYSVC_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say this is a test"},
        ],
    },
)
response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
