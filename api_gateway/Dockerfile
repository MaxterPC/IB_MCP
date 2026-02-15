FROM eclipse-temurin:21

WORKDIR /app

# Install unzip
RUN apt-get update && apt-get install -y unzip

# Download and unzip client portal gateway
# NOTE: Update GATEWAY_SHA256 when upgrading the gateway version.
# Generate with: sha256sum clientportal.gw.zip
ARG GATEWAY_SHA256=""
RUN mkdir api_gateway && cd api_gateway && \
    curl -O https://download2.interactivebrokers.com/portal/clientportal.gw.zip && \
    if [ -n "$GATEWAY_SHA256" ]; then \
      echo "$GATEWAY_SHA256  clientportal.gw.zip" | sha256sum -c - || exit 1; \
    else \
      echo "WARNING: No GATEWAY_SHA256 provided, skipping checksum verification"; \
    fi && \
    unzip clientportal.gw.zip && rm clientportal.gw.zip

# Create the directory where the config file is expected
RUN mkdir -p api_gateway/root

# Copy our config so that the gateway will use it
COPY conf.yaml api_gateway/root/conf.yaml

# Make the entrypoint script executable
COPY run_gateway.sh /app/run_gateway.sh
RUN chmod +x /app/run_gateway.sh

# Copy the healthcheck script and make it executable
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Copy the tickler script and make it executable
COPY tickler.sh /app/tickler.sh
RUN chmod +x /app/tickler.sh

# Install curl for the tickler script
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create non-root user and set ownership
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5055

ENTRYPOINT ["/app/run_gateway.sh", "api_gateway/root/conf.yaml"]

CMD api_gateway/bin/run.sh api_gateway/root/conf.yaml
