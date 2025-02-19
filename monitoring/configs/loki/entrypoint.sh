#!/bin/sh

# Define the path to the template configuration file
CONFIG_TEMPLATE_FILE="/etc/loki/loki-config.yaml.template"
CONFIG_FILE="/etc/loki/loki-config.yaml"

# Replace placeholders with environment variables
sed -i "s|\${ALERTMANAGER_HOST}|${ALERTMANAGER_HOST}|g" $CONFIG_TEMPLATE_FILE
sed -i "s|\${ALERTMANAGER_PORT}|${ALERTMANAGER_PORT}|g" $CONFIG_TEMPLATE_FILE

# Copy the processed file to the actual config file location
cp $CONFIG_TEMPLATE_FILE $CONFIG_FILE

# Start Loki with the processed config file
exec /usr/bin/loki -config.file=$CONFIG_FILE
