import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
IMAGE_URL = os.environ.get(
    "IMAGE_URL",
    "https://upload.wikimedia.org/wikipedia/commons/3/3a/Cat03.jpg",
)
PROMPT = os.environ.get("PROMPT", "Describe this image.")

response = requests.post(
    f"{SERVICE_BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {UNITYSVC_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": IMAGE_URL}},
                ],
            }
        ],
    },
)
response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
