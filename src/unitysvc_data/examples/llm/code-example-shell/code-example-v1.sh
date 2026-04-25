#!/bin/bash
# Chat completion request against an OpenAI-compatible LLM endpoint.
#
# Required environment variables:
#   SERVICE_BASE_URL — chat-completion endpoint (gateway or upstream)
#   UNITYSVC_API_KEY — bearer token (customer key in gateway mode,
#                      upstream key in local-testing mode)
#   MODEL            — interface-specific model identifier (the
#                      gateway and the upstream may use different
#                      strings, so this must come from the caller)
set -e
set -o pipefail

: "${SERVICE_BASE_URL:?SERVICE_BASE_URL is not set}"
: "${UNITYSVC_API_KEY:?UNITYSVC_API_KEY is not set}"
: "${MODEL:?MODEL is not set}"

curl -sS "${SERVICE_BASE_URL}" \
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
