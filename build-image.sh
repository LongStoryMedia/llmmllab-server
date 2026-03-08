#!/bin/bash

set -e

# Usage: ./build-image.sh <platform>
# <platform>: multi-arch (default), or lsnode-3 (for GPU-specific builds)

REGISTRY=${REGISTRY:-192.168.0.71:31500}
TAG=${TAG:-latest}

PLATFORM=${1:-multi-arch}

if [ "$PLATFORM" != "multi-arch" ] && [ "$PLATFORM" != "lsnode-3" ]; then
    echo "Error: Platform must be multi-arch or lsnode-3"
    exit 1
fi

echo "Building server image with platform: $PLATFORM"

if [ "$PLATFORM" = "lsnode-3" ]; then
    # GPU-specific build on lsnode-3
    echo "Building server image on lsnode-3 (AMD64)..."
    ssh root@lsnode-3.local "
      TEMP_DIR=\$(mktemp -d)
      trap 'rm -rf \${TEMP_DIR}' EXIT
      echo \"Created temp directory: \${TEMP_DIR}\"

      echo \"Syncing code to temp directory...\"
      cp -r /data/code-base/* \${TEMP_DIR}/

      echo \"Building server image...\"
      cd \${TEMP_DIR}/server && docker build -t \${REGISTRY}/server:\${TAG} -f k8s/Dockerfile . --push

      echo \"server image built and pushed: \${REGISTRY}/server:\${TAG}\"
    "
else
    # Multi-arch build
    echo "Building server multi-arch image (linux/amd64, linux/arm64)..."
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t ${REGISTRY}/server:${TAG} \
        --push \
        -f k8s/Dockerfile .
fi

echo "server build complete: ${REGISTRY}/server:${TAG}"