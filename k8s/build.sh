#!/bin/bash

set -e

REGISTRY=${REGISTRY:-192.168.0.71:31500}
TAG=${TAG:-latest}

# Build multi-arch image for server (runs on any node, no GPU requirements)
# Supports both ARM64 (lsnode-0,1,2) and AMD64 (lsnode-3)
echo "Building server multi-arch image (linux/amd64, linux/arm64)..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    -t ${REGISTRY}/server:${TAG} \
    --push \
    -f k8s/Dockerfile .

echo "Server multi-arch image built and pushed: ${REGISTRY}/server:${TAG}"