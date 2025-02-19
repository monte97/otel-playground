#!/bin/sh
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
# Define the path to the template and the output file
TEMPLATE_FILE="./configs/tempo/tempo-config.yaml.template"
OUTPUT_FILE="./configs/tempo/tempo-config.yaml"

# Replace placeholders with environment variable values and write to the output file
sed "s|\${TEMPO_PORT_HTTP}|${TEMPO_PORT_HTTP}|g" $TEMPLATE_FILE | \
sed "s|\${TEMPO_PORT_OLTP}|${TEMPO_PORT_OLTP}|g" | \
sed "s|\${PROMETHEUS_HOST}|${PROMETHEUS_HOST}|g" | \
sed "s|\${PROMETHEUS_PORT}|${PROMETHEUS_PORT}|g" > $OUTPUT_FILE
