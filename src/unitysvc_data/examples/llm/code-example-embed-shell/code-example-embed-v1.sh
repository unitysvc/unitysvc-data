#!/bin/bash
# Embeddings request against an OpenAI-compatible endpoint.
#
# Required environment variables:
#   SERVICE_BASE_URL — embeddings endpoint
#   UNITYSVC_API_KEY — bearer token
#   MODEL            — interface-specific model identifier (the
#                      gateway and upstream may use different
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
  "input": ["Embed this sentence.", "As well as this one."]
}
EOF
)"
