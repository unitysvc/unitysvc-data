import json
import os

import requests

UNITYSVC_API_KEY = os.environ["UNITYSVC_API_KEY"]
SERVICE_BASE_URL = os.environ["SERVICE_BASE_URL"]
MODEL = os.environ["MODEL"]


def echo_message(message: str) -> str:
    return f"Echo: {message}"


response = requests.post(
    f"{SERVICE_BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {UNITYSVC_API_KEY}",
        "Content-Type": "application/json",
    },
    json={
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
                            "message": {"type": "string", "description": "The message to echo"},
                        },
                        "required": ["message"],
                    },
                },
            }
        ],
        "tool_choice": "auto",
    },
)
response.raise_for_status()

message = response.json()["choices"][0]["message"]
tool_calls = message.get("tool_calls") or []
if tool_calls:
    for tool_call in tool_calls:
        args = json.loads(tool_call["function"]["arguments"])
        if tool_call["function"]["name"] == "echo_message":
            print(echo_message(args["message"]))
else:
    print(message.get("content", ""))
