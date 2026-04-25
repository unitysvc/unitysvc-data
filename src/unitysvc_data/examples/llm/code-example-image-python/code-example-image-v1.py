import base64
import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
PROMPT = os.environ.get("PROMPT", "An astronaut riding a horse on Mars")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "image.png")

headers = {
    "Authorization": f"Bearer {UNITYSVC_API_KEY}",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "prompt": PROMPT,
    "n": 1,
    "size": "1024x1024",
    "response_format": "b64_json",
}

response = requests.post(SERVICE_BASE_URL, headers=headers, json=payload)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
    raise SystemExit(1)

data = response.json()["data"][0]
if "b64_json" in data:
    with open(OUTPUT_FILE, "wb") as f:
        f.write(base64.b64decode(data["b64_json"]))
    print(f"Saved {OUTPUT_FILE}")
elif "url" in data:
    print(data["url"])
else:
    print(response.text)
