#!/bin/bash
set -e -o pipefail

: "${SERVICE_BASE_URL:?SERVICE_BASE_URL is not set}"
: "${UNITYSVC_API_KEY:?UNITYSVC_API_KEY is not set}"
: "${MODEL:?MODEL is not set}"

curl --fail-with-body -sS "${SERVICE_BASE_URL}/embeddings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${UNITYSVC_API_KEY}" \
  -d @- <<EOF
{
  "model": "${MODEL}",
  "input": ["Embed this sentence.", "As well as this one."]
}
EOF
