#!/bin/bash

# Inject SSL password from environment variable into a writable copy of the config
cp /app/api_gateway/root/conf.yaml /tmp/conf.yaml
if [ -n "$SSL_PASSWORD" ]; then
  sed -i "s/SSL_PASSWORD_PLACEHOLDER/$SSL_PASSWORD/g" /tmp/conf.yaml
else
  sed -i "s/SSL_PASSWORD_PLACEHOLDER/mywebapi/g" /tmp/conf.yaml
fi

# Start the API Gateway in the background using the processed config
cd /app/api_gateway
sh bin/run.sh /tmp/conf.yaml &

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