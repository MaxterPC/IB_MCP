#!/bin/sh
# This script contains the tickler logic to keep the API Gateway session alive.
# It continuously sends POST requests to the tickle endpoint at a specified interval.

echo "[tickler] Tickler service started."

# Determine SSL flags: use CA cert if available, otherwise fall back to -k (insecure)
CURL_SSL_FLAGS="-k"
if [ -n "$GATEWAY_CA_CERT" ] && [ -f "$GATEWAY_CA_CERT" ]; then
  CURL_SSL_FLAGS="--cacert $GATEWAY_CA_CERT"
  echo "[tickler] Using CA certificate: $GATEWAY_CA_CERT"
fi

while true; do
  NOW=$(date)
  echo "[tickler] $NOW: Sending tickle to ${TICKLE_BASE_URL}${TICKLE_ENDPOINT}"

  curl -s $CURL_SSL_FLAGS -X POST "${TICKLE_BASE_URL}${TICKLE_ENDPOINT}" -H "Content-Type: application/json" -d "{}" -w " HTTP status: %{http_code}\n"

  sleep "${TICKLE_INTERVAL}"
done
