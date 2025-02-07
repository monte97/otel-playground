#!/bin/sh

echo ${OTEL_COLLECTOR_HOST}

# Define the path to the template and the output file
TEMPLATE_FILE="./configs/tempo/tempo-config.yaml.template"
OUTPUT_FILE="./configs/tempo/tempo-config.yaml"

# Replace placeholders with environment variable values and write to the output file
sed "s|\${OTEL_COLLECTOR_HOST}|${OTEL_COLLECTOR_HOST}|g" $TEMPLATE_FILE | \
sed "s|\${OTEL_COLLECTOR_PORT_GRPC}|${OTEL_COLLECTOR_PORT_GRPC}|g" | \
sed "s|\${OTEL_COLLECTOR_PORT_HTTP}|${OTEL_COLLECTOR_PORT_HTTP}|g" | \
sed "s|\${PROMETHEUS_HOST}|${PROMETHEUS_HOST}|g" | \
sed "s|\${PROMETHEUS_PORT}|${PROMETHEUS_PORT}|g" > $OUTPUT_FILE
