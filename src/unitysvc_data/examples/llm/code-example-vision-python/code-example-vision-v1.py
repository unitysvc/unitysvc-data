import base64
import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
IMAGE_FILE = os.environ.get("IMAGE_FILE", "image.jpg")
PROMPT = os.environ.get("PROMPT", "Describe this image.")

with open(IMAGE_FILE, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("ascii")

response = requests.post(
    SERVICE_BASE_URL,
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
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            }
        ],
    },
)
response.raise_for_status()
print(response.json()["choices"][0]["message"]["content"])
