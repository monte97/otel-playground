#!/bin/bash

RELEASE=${1:-latest}

docker buildx build -f configs/Dockerfile configs --tag grafana/otel-lgtm:"${RELEASE}"
