#!/bin/bash
set -e -o pipefail

: "${SERVICE_BASE_URL:?SERVICE_BASE_URL is not set}"
: "${UNITYSVC_API_KEY:?UNITYSVC_API_KEY is not set}"
: "${MODEL:?MODEL is not set}"

curl --fail-with-body -sS "${SERVICE_BASE_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${UNITYSVC_API_KEY}" \
  -d "$(cat <<EOF
{
  "model": "${MODEL}",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Say this is a test"}
  ]
}
EOF
)"
