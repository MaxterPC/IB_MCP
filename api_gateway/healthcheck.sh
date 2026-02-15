#!/bin/sh
# This script performs a health check for the API Gateway service.
# It checks if the API Gateway is reachable and returns a valid JSON response.

URL="${GATEWAY_INTERNAL_BASE_URL}:${GATEWAY_PORT}${GATEWAY_TEST_ENDPOINT}"

# Determine SSL flags: use CA cert if available, otherwise fall back to -k (insecure)
CURL_SSL_FLAGS="-k"
if [ -n "$GATEWAY_CA_CERT" ] && [ -f "$GATEWAY_CA_CERT" ]; then
  CURL_SSL_FLAGS="--cacert $GATEWAY_CA_CERT"
fi

echo "Attempting to check API Gateway health at: $URL"

# Use a secure temp file instead of a predictable path
TMPFILE=$(mktemp /tmp/healthcheck.XXXXXX)
trap "rm -f $TMPFILE" EXIT

STATUS=$(curl -s $CURL_SSL_FLAGS -w "%{http_code}" -o "$TMPFILE" "$URL")

if [ "$STATUS" -ne 401 ]; then
  if grep -q "{" "$TMPFILE"; then
    echo "API Gateway healthcheck successful: HTTP status $STATUS, response contains JSON."
    exit 0
  else
    echo "API Gateway healthcheck failed: Response does not contain a JSON object."
    exit 1
  fi
else
  echo "API Gateway healthcheck failed: Received HTTP status $STATUS (expected non-401)."
  exit 1
fi
