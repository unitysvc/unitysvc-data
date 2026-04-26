import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
VOICE = os.environ.get("VOICE", "alloy")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "tts_output.wav")

response = requests.post(
    f"{SERVICE_BASE_URL}/audio/speech",
    headers={
        "Authorization": f"Bearer {UNITYSVC_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL,
        "input": "I love building and shipping new features for our users!",
        "voice": VOICE,
        "response_format": "wav",
    },
)
response.raise_for_status()

with open(OUTPUT_FILE, "wb") as f:
    f.write(response.content)
print(f"Saved {OUTPUT_FILE}")
