#!/bin/bash

set -e

NS="llmmll"

echo "Creating namespace $NS if it doesn't exist..."
kubectl create namespace $NS --dry-run=client -o yaml | kubectl apply -f -

echo "Creating secrets..."
# Get secrets from psql namespace
DB_PASSWORD=$(kubectl get secret secrets -n psql -o jsonpath='{.data.psqlpw}' | base64 --decode)

# Create secrets for DB access
kubectl create secret generic db-credentials \
  -n $NS \
  --from-literal=password="$DB_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Applying PostgreSQL manifests..."
kubectl apply -f server/k8s/psql/serviceaccount.yaml -n $NS
kubectl apply -f server/k8s/psql/dbs.yaml -n $NS
kubectl apply -f server/k8s/psql/pgadmin-servers.yaml -n $NS
kubectl apply -f server/k8s/psql/pvc.yaml -n $NS
kubectl apply -f server/k8s/psql/statefulset.yaml -n $NS
kubectl apply -f server/k8s/psql/service.yaml -n $NS
kubectl apply -f server/k8s/psql/pgadmin.yaml -n $NS
kubectl apply -f server/k8s/psql/referencegrant.yaml -n $NS

echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=Ready pod -l app=psql -n $NS --timeout=300s

echo "PostgreSQL installation complete!"
echo "Service: postgres.$NS.svc.cluster.local:5432"
echo "pgAdmin: Port forward with 'kubectl port-forward svc/pgadmin -n $NS 8084:8084'"