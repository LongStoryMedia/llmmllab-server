#!/bin/bash

set -e

DOCKER_TAG=${DOCKER_TAG:-main}
# Replace slashes with dots in the tag name for Docker compatibility
DOCKER_TAG=$(echo "$DOCKER_TAG" | tr '/' '.')
echo "Deploying server with tag: $DOCKER_TAG"

# Create the namespace if it doesn't exist
kubectl create namespace llmmll || true

# Get secrets from other namespaces
DB_PASSWORD=$(kubectl get secret secrets -n psql -o jsonpath='{.data.psqlpw}' | base64 --decode)
CLIENT_SECRET=$(kubectl get secret client-secret -n auth -o jsonpath='{.data.client-secret}' | base64 --decode)

# Create secrets for DB access
kubectl create secret generic db-credentials \
-n llmmll \
--from-literal=password="$DB_PASSWORD" \
--dry-run=client -o yaml | kubectl apply -f - --wait=true

# Create secrets for auth client
kubectl create secret generic auth-client \
-n llmmll \
--from-literal=client_secret="$CLIENT_SECRET" \
--dry-run=client -o yaml | kubectl apply -f - --wait=true

if [ ! -d "$(dirname "$0")/.secrets" ]; then
    mkdir -p "$(dirname "$0")/.secrets"
fi

if [ ! -f "$(dirname "$0")/.secrets/internal-api-key" ]; then
    openssl rand -hex 16 > "$(dirname "$0")/.secrets/internal-api-key"
fi

# Create secrets for internal API access
kubectl create secret generic internal-api-key \
-n llmmll \
--from-file=api_key="$(dirname "$0")/.secrets/internal-api-key" \
--dry-run=client -o yaml | kubectl apply -f - --wait=true

# Create secret for HuggingFace token
if [ -f "$(dirname "$0")/.secrets/hf-token" ]; then
    HF_TOKEN=$(cat "$(dirname "$0")/.secrets/hf-token")
    kubectl create secret generic hf-token \
    -n llmmll \
    --from-literal=token="$HF_TOKEN" \
    --dry-run=client -o yaml | kubectl apply -f - --wait=true
else
    echo "WARNING: .secrets/hf-token not found — HF_TOKEN secret will not be created"
fi

echo "Updating deployment image to use tag: $DOCKER_TAG"
# Create a temporary file with the updated image tag
sed "s|image: 192.168.0.71:31500/server:.*|image: 192.168.0.71:31500/server:$DOCKER_TAG|g" "$(dirname "$0")/deployment.yaml" > "$(dirname "$0")/deployment.yaml.tmp"
mv "$(dirname "$0")/deployment.yaml.tmp" "$(dirname "$0")/deployment.yaml"

echo "Applying deployment..."
kubectl apply -f "$(dirname "$0")/deployment.yaml" -n llmmll --wait=true

echo "Applying service..."
kubectl apply -f "$(dirname "$0")/service.yaml" -n llmmll --wait=true

echo "Deployment complete! Server service is available at llmmll-server.llmmll.svc.cluster.local:8000"