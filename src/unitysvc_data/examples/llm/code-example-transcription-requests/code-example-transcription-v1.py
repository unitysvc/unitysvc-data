import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]
AUDIO_URL = os.environ.get(
    "AUDIO_URL",
    "https://raw.githubusercontent.com/openai/whisper/main/tests/jfk.flac",
)

audio = requests.get(AUDIO_URL, timeout=30)
audio.raise_for_status()
filename = AUDIO_URL.rsplit("/", 1)[-1].split("?")[0] or "audio"

response = requests.post(
    SERVICE_BASE_URL,
    headers={"Authorization": f"Bearer {UNITYSVC_API_KEY}"},
    files={
        "file": (filename, audio.content),
        "model": (None, MODEL),
    },
)
response.raise_for_status()
print(response.json()["text"])
