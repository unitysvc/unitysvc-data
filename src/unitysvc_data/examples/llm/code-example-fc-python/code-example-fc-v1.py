import json
import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]

headers = {
    "Authorization": f"Bearer {UNITYSVC_API_KEY}",
    "Content-Type": "application/json",
}


def echo_message(message: str) -> str:
    return f"Echo: {message}"


data = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Echo back: this is a test"},
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "echo_message",
                "description": "Echoes back the given message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to echo",
                        }
                    },
                    "required": ["message"],
                },
            },
        }
    ],
    "tool_choice": "auto",
}

response = requests.post(SERVICE_BASE_URL, headers=headers, json=data)

if response.status_code != 200:
    print(f"Error {response.status_code}: {response.text}")
    raise SystemExit(1)

message = response.json()["choices"][0]["message"]

if message.get("tool_calls"):
    for tool_call in message["tool_calls"]:
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        if name == "echo_message":
            print(echo_message(args["message"]))
else:
    print(message.get("content", ""))
