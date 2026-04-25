import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]

headers = {
    "Authorization": f"Bearer {UNITYSVC_API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say this is a test"},
    ],
}

response = requests.post(SERVICE_BASE_URL, headers=headers, json=data)

if response.status_code == 200:
    completion = response.json()
    print(completion["choices"][0]["message"]["content"])
else:
    print(f"Error {response.status_code}: {response.text}")
