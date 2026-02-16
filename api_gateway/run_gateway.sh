#!/bin/bash

# Inject SSL password from environment variable into the config
# Note: sed -i fails on Docker overlay fs, so we use redirect + cp
CONF=/app/api_gateway/root/conf.yaml
if [ -n "$SSL_PASSWORD" ]; then
  sed "s/SSL_PASSWORD_PLACEHOLDER/$SSL_PASSWORD/g" "$CONF" > /tmp/conf.yaml && cp /tmp/conf.yaml "$CONF"
else
  sed "s/SSL_PASSWORD_PLACEHOLDER/mywebapi/g" "$CONF" > /tmp/conf.yaml && cp /tmp/conf.yaml "$CONF"
fi

# Start the API Gateway in the background using the processed config
cd /app/api_gateway
sh bin/run.sh root/conf.yaml &

# Wait for the API Gateway to become healthy before starting the tickler
echo "Waiting for API Gateway to become healthy..."
while ! /usr/local/bin/healthcheck.sh > /dev/null 2>&1; do
  echo "API Gateway not ready yet, waiting..."
  sleep 2
done

echo "API Gateway is healthy, starting tickler..."
/app/tickler.sh &

# Wait for the API Gateway process to keep container alive
wait