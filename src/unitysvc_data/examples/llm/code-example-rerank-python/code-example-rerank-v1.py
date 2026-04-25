import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]

headers = {
    "Authorization": f"Bearer {UNITYSVC_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

payload = {
    "model": MODEL,
    "query": "What is the capital of the United States?",
    "top_n": 3,
    "documents": [
        "Carson City is the capital of Nevada.",
        "Saipan is the capital of the Northern Mariana Islands.",
        "Washington, D.C. is the capital of the United States.",
        "Capitalization is the use of a capital letter at the start of a word.",
        "Capital punishment has existed in the United States for centuries.",
    ],
}

response = requests.post(SERVICE_BASE_URL, headers=headers, json=payload)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
    raise SystemExit(1)

print(response.json())
