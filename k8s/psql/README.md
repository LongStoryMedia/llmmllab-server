# PostgreSQL for llmmllab Server

This directory contains Kubernetes manifests for the PostgreSQL database used by the llmmllab server.

## Overview

The PostgreSQL deployment provides:
- TimescaleDB for time-series data support
- Multiple databases: `ollama`, `llmmll`
- pgAdmin for database management
- Persistent storage (300Gi PVC)

## Directory Structure

```
server/k8s/psql/
├── README.md           # This file
├── statefulset.yaml    # PostgreSQL StatefulSet
├── service.yaml        # PostgreSQL Service
├── pvc.yaml            # PersistentVolumeClaim
├── serviceaccount.yaml # ServiceAccount
├── dbs.yaml            # Database initialization ConfigMap
├── pgadmin.yaml        # pgAdmin Deployment and Service
├── pgadmin-servers.yaml # pgAdmin server configuration
├── referencegrant.yaml # ReferenceGrant for pgAdmin access
└── install.sh          # Installation script
```

## Configuration

### Database Settings

- **User**: `lsm`
- **Password**: Retrieved from `secrets` secret in `psql` namespace
- **Databases**: `ollama`, `llmmll`
- **Port**: 5432

### Resource Limits

- **CPU**: 100m - 3 cores
- **Memory**: 128Mi - 6Gi
- **Storage**: 300Gi

## Deployment

```bash
# Install to the llmmll namespace
kubectl apply -f server/k8s/psql/ -n llmmll

# Or apply individual manifests
kubectl apply -f server/k8s/psql/statefulset.yaml -n llmmll
kubectl apply -f server/k8s/psql/service.yaml -n llmmll
kubectl apply -f server/k8s/psql/dbs.yaml -n llmmll
```

## Accessing the Database

### From within the cluster

```
Host: postgres.llmmll.svc.cluster.local
Port: 5432
Database: llmmll
User: lsm
Password: <from secrets>
```

### Using pgAdmin

```bash
# Port-forward pgAdmin
kubectl port-forward svc/pgadmin -n llmmll 8084:8084

# Access at http://localhost:8084
# Email: longstoryscott@gmail.com
# Password: <from secrets>
```

## Maintenance

### Check PostgreSQL status

```bash
kubectl get statefulset -n llmmll
kubectl get pods -n llmmll -l app=psql
```

### View logs

```bash
kubectl logs -n llmmll <psql-pod-name>
```

### Run SQL commands

```bash
kubectl exec -it -n llmmll <psql-pod-name> -- psql -U lsm -d llmmll
```

## Migration from psql namespace

To migrate from the existing `psql` namespace:

1. Export data from existing database
2. Apply new manifests to `llmmll` namespace
3. Import data to new database
4. Update server configuration to use new host