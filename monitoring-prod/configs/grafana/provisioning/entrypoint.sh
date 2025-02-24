#!/bin/bash

# Define the path to the template and the output file
TEMPLATE_FILE="/etc/grafana/provisioning/datasources/grafana-datasources.yaml.template"
OUTPUT_FILE="/etc/grafana/provisioning/datasources/grafana-datasources.yaml"

# Replace placeholders with environment variable values and write to the output file
sed "s|\${PROMETHEUS_HOST}|${PROMETHEUS_HOST}|g" $TEMPLATE_FILE | \
sed "s|\${PROMETHEUS_PORT}|${PROMETHEUS_PORT}|g" | \
sed "s|\${TEMPO_HOST}|${TEMPO_HOST}|g" | \
sed "s|\${TEMPO_PORT}|${TEMPO_PORT}|g" | \
sed "s|\${LOKI_HOST}|${LOKI_HOST}|g" | \
sed "s|\${LOKI_PORT}|${LOKI_PORT}|g" > $OUTPUT_FILE

# Start Grafana server
exec grafana-server
