import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
AUDIO_FILE = os.environ.get("AUDIO_FILE", "audio.mp3")

with open(AUDIO_FILE, "rb") as f:
    response = requests.post(
        SERVICE_BASE_URL,
        headers={"Authorization": f"Bearer {UNITYSVC_API_KEY}"},
        files={
            "file": (os.path.basename(AUDIO_FILE), f),
            "model": (None, MODEL),
        },
    )
response.raise_for_status()
print(response.json()["text"])
