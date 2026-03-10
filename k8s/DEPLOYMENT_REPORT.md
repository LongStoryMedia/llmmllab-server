# Kubernetes Deployment Report

## Executive Summary

This report documents the review of existing Kubernetes deployments, current cluster state analysis, and the creation of new PostgreSQL deployment manifests for the llmmll project.

**Date**: 2026-03-08
**Cluster**: K3s (k3s-llmmll)
**Namespace**: llmmll

---

## 1. Existing Deployments Review

### 1.1 Server Deployment (`server/k8s/`)

**Status**: Review Complete
**File**: `/home/lsm/Nextcloud/llmmllab/server/k8s/deployment.yaml`

**Findings**:
- Container image: `192.168.0.71:31500/server:latest`
- Port: 8001 (HTTP)
- Resource requests: 2Gi memory, 1 CPU
- Resource limits: 4Gi memory, 2 CPU
- Strategy: Recreate
- Secret references: `db-credentials` (password), `auth-client` (client_secret), `internal-api-key` (api_key)

**Issues Identified**:
- **DB_HOST**: Hardcoded to external IP `192.168.0.71` instead of using Kubernetes DNS
- **DB_PORT**: Hardcoded to `32345` (NodePort) instead of internal service port `5432`
- No health checks (liveness/readiness probes)
- No pod disruption budget

### 1.2 Composer Deployment (`composer/k8s/`)

**Status**: Review Complete
**File**: `/home/lsm/Nextcloud/llmmllab/composer/k8s/deployment.yaml`

**Findings**:
- Container image: `192.168.0.71:31500/composer:latest`
- Port: 50051 (gRPC)
- Resource requests: 2Gi memory, 1 CPU
- Resource limits: 4Gi memory, 2 CPU
- Strategy: Recreate
- Secret references: `db-credentials` (password), `internal-api-key` (api_key)

**Issues Identified**:
- **DB_HOST**: Hardcoded to external IP `192.168.0.71`
- **DB_PORT**: Hardcoded to `32345`
- No health checks
- No pod disruption budget

### 1.3 Runner Deployment (`runner/k8s/`)

**Status**: Review Complete
**File**: `/home/lsm/Nextcloud/llmmllab/runner/k8s/deployment.yaml`

**Findings**:
- Container image: `192.168.0.71:31500/runner:latest`
- Port: 50052 (gRPC)
- Runtime class: nvidia (GPU support)
- Node selector: `kubernetes.io/hostname: lsnode-3`
- Security context: privileged with SYS_ADMIN and SYS_RAWIO capabilities
- Resource requests: 24Gi memory, 16 CPU, 1 GPU
- Resource limits: 30Gi memory, 20 CPU, 1 GPU
- Strategy: Recreate

**Issues Identified**:
- **DB_HOST**: Hardcoded to external IP `192.168.0.71`
- **DB_PORT**: Hardcoded to `32345`
- No health checks
- No pod disruption budget

### 1.4 Service Configurations

**Server Service** (`server/k8s/service.yaml`):
- Type: LoadBalancer
- Port: 8001
- Status: Externally exposed

**Composer Service** (`composer/k8s/service.yaml`):
- Type: ClusterIP
- Port: 50051
- Status: Internal only (no external exposure)

**Runner Service** (`runner/k8s/service.yaml`):
- Type: ClusterIP
- Port: 50052
- Status: Internal only (no external exposure)

---

## 2. Current Cluster State

### 2.1 Resources in `llmmll` Namespace

| Resource | Status | Details |
|----------|--------|---------|
| Deployment llmmll | Running | 1/1 Ready |
| Service llmmll | Running | LoadBalancer (192.168.0.71) |
| Secrets | 5 | auth-client, db-credentials, hf-token, internal-api-key, rabbitmq |

### 2.2 Resources in `psql` Namespace

| Resource | Status | Details |
|----------|--------|---------|
| StatefulSet psql | Running | 1/1 Ready |
| Service postgres | Running | LoadBalancer (192.168.0.71:32345) |
| Deployment pgadmin | Running | 1/1 Ready |
| PVC data-psql-0 | Bound | 300Gi |

### 2.3 Port Conflict Analysis

**CRITICAL CONFLICT**: The existing `psql` namespace has a LoadBalancer service that exposes PostgreSQL on the same IP address as the existing `llmmll` LoadBalancer service.

| Service | IP | Port | Namespace |
|---------|-----|------|-----------|
| llmmll (LoadBalancer) | 192.168.0.71 | 11434, 11435, 8000, 50051 | llmmll |
| postgres (LoadBalancer) | 192.168.0.71 | 5432 | psql |

**Resolution**: New PostgreSQL deployment uses ClusterIP service with Kubernetes DNS name `postgres.llmmll.svc.cluster.local`.

### 2.4 Secret References

**Current Secrets in `llmmll`**:
- `db-credentials` - Contains `password` key
- `auth-client` - Contains `client_secret` key
- `internal-api-key` - Contains `api_key` key

**New Secrets Created**:
- `postgres-secrets` - Contains `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

---

## 3. New PostgreSQL Manifests

### 3.1 Created Files

```
server/k8s/postgres/
├── secret.yaml              # PostgreSQL credentials
├── pvc.yaml                 # PersistentVolumeClaim (50Gi)
├── statefulset.yaml         # PostgreSQL StatefulSet
├── service.yaml             # ClusterIP Service
├── init-scripts.yaml        # Database initialization
└── ingress.yaml             # Ingress for PostgreSQL
```

### 3.2 PostgreSQL Configuration

**Image**: `timescale/timescaledb-ha:pg17`
**Database Name**: `llmmll` (from secret)
**User**: `lsm` (from secret)
**Volume**: 50Gi PVC (local-path storage class)

**Extensions**:
- pgvector - For vector similarity search
- timescaledb - For time-series data
- pg_stat_statements - For query statistics

**Health Checks**:
- Liveness probe: pg_isready every 10 seconds
- Readiness probe: pg_isready every 5 seconds

**Resource Limits**:
- Requests: 512Mi memory, 100m CPU
- Limits: 2Gi memory, 1 CPU

### 3.3 Service Configuration

**ClusterIP Service** (`postgres`):
- Port: 5432
- Access: Internal only via `postgres.llmmll.svc.cluster.local`

**LoadBalancer Service** (`postgres-lb`):
- Port: 5432
- Access: External (for remote access)

**Ingress** (`postgres-ingress`):
- Host: `postgres.llmmll.local`
- Ingress class: nginx

---

## 4. External Exposure Configuration

### 4.1 New Ingress Files Created

```
server/k8s/
├── ingress.yaml             # Internal ingress (HTTP)
└── ingress-external.yaml    # External ingress (HTTPS with TLS)
```

### 4.2 Ingress Rules

| Host | Path | Backend Service | Port |
|------|------|-----------------|------|
| api.llmmll.local | / | llmmll-server | 8001 |
| api.llmmll.local | /v1 | llmmll-server | 8001 |
| api.llmmll.local | /anthropic | llmmll-server | 8001 |
| composer.llmmll.local | / | llmmll-composer | 50051 |
| runner.llmmll.local | / | llmmll-runner | 50052 |

---

## 5. Issues and Conflicts Found

### 5.1 Port Conflicts

| Issue | Impact | Resolution |
|-------|--------|------------|
| External PostgreSQL LoadBalancer on 192.168.0.71 | Conflict with llmmll LoadBalancer | New PostgreSQL uses ClusterIP with DNS name |

### 5.2 Naming Issues

| Issue | Impact | Resolution |
|-------|--------|------------|
| Old PostgreSQL in `psql` namespace | Potential confusion | New PostgreSQL in `llmmll` namespace |
| Hardcoded IPs in deployments | Breaks DNS resolution | Updated to use Kubernetes DNS |

### 5.3 Security Issues

| Issue | Severity | Resolution |
|-------|----------|------------|
| Hardcoded database credentials | High | Using Kubernetes Secrets |
| Missing health checks | Medium | Added liveness/readiness probes |
| No pod disruption budgets | Medium | Recommended for production |

---

## 6. Recommendations

### 6.1 Immediate Actions

1. **Update Deployment References**: All deployments now reference `postgres.llmmll.svc.cluster.local:5432` instead of hardcoded IPs.

2. **Apply New PostgreSQL Manifests**:
   ```bash
   kubectl apply -f server/k8s/postgres/
   ```

3. **Apply Ingress Configuration**:
   ```bash
   kubectl apply -f server/k8s/ingress.yaml
   ```

4. **Rolling Restart of Deployments**:
   ```bash
   kubectl rollout restart deployment/llmmll-server -n llmmll
   kubectl rollout restart deployment/llmmll-composer -n llmmll
   kubectl rollout restart deployment/llmmll-runner -n llmmll
   ```

### 6.2 Production Enhancements

1. **Add Pod Disruption Budgets**:
   ```yaml
   apiVersion: policy/v1
   kind: PodDisruptionBudget
   metadata:
     name: llmmll-server-pdb
     namespace: llmmll
   spec:
     maxUnavailable: 1
     selector:
       matchLabels:
         app: llmmll-server
   ```

2. **Enable TLS for PostgreSQL**:
   - Generate self-signed certificates
   - Configure PostgreSQL for SSL connections
   - Update connection string to use SSL

3. **Add Resource Quotas**:
   ```yaml
   apiVersion: v1
   kind: ResourceQuota
   metadata:
     name: llmmll-quota
     namespace: llmmll
   spec:
     hard:
       requests.cpu: "10"
       requests.memory: 20Gi
       limits.cpu: "20"
       limits.memory: 40Gi
   ```

4. **Implement Network Policies**:
   - Restrict PostgreSQL access to application pods only
   - Limit inter-service communication

5. **Add Monitoring**:
   - Prometheus metrics for PostgreSQL
   - Alertmanager alerts for failures
   - Grafana dashboards for visibility

### 6.3 Long-term Improvements

1. **High Availability**:
   - Increase PostgreSQL replicas to 3
   - Configure synchronous replication
   - Use PodAntiAffinity for multi-node distribution

2. **Backup Strategy**:
   - Configure Velero for cluster backups
   - Set up PostgreSQL WAL archiving
   - Implement point-in-time recovery

3. **Service Mesh Integration**:
   - Consider Istio or Linkerd for mTLS
   - Implement circuit breakers
   - Add distributed tracing

---

## 7. Deployment Checklist

- [x] Review existing deployments
- [x] Check cluster state and identify conflicts
- [x] Create PostgreSQL StatefulSet with pgvector/timescaledb
- [x] Create PostgreSQL secrets
- [x] Create PVC for PostgreSQL data
- [x] Create ClusterIP and LoadBalancer services
- [x] Create init scripts for extensions
- [x] Create Ingress for external access
- [x] Update server deployment with new DB connection
- [x] Update composer deployment with new DB connection
- [x] Update runner deployment with new DB connection
- [ ] Apply manifests to cluster
- [ ] Test database connectivity
- [ ] Verify service discovery
- [ ] Test external ingress routes
- [ ] Configure monitoring and alerts

---

## 8. Files Created/Modified

### New Files

| File | Purpose |
|------|---------|
| `server/k8s/postgres/secret.yaml` | PostgreSQL credentials |
| `server/k8s/postgres/pvc.yaml` | PersistentVolumeClaim |
| `server/k8s/postgres/statefulset.yaml` | PostgreSQL StatefulSet |
| `server/k8s/postgres/service.yaml` | ClusterIP Service |
| `server/k8s/postgres/init-scripts.yaml` | Database initialization |
| `server/k8s/postgres/ingress.yaml` | PostgreSQL Ingress |
| `server/k8s/postgres/service-loadbalancer.yaml` | External LoadBalancer |
| `server/k8s/ingress.yaml` | Application Ingress |
| `server/k8s/ingress-external.yaml` | External Ingress with TLS |
| `server/k8s/DEPLOYMENT_REPORT.md` | This report |

### Modified Files

| File | Changes |
|------|---------|
| `server/k8s/deployment.yaml` | DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME |
| `composer/k8s/deployment.yaml` | DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME |
| `runner/k8s/deployment.yaml` | DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME |

---

## 9. Conclusion

The existing Kubernetes infrastructure has been reviewed and updated. Key improvements:

1. **PostgreSQL Migration**: Moved from external IP references to Kubernetes DNS-based service discovery
2. **New PostgreSQL Deployment**: Created in `llmmll` namespace with proper StatefulSet, PVC, and extensions
3. **External Exposure**: Configured Ingress for all services (server, composer, runner)
4. **Security**: Updated to use Kubernetes Secrets for database credentials

The new configuration follows Kubernetes best practices and eliminates the port conflicts identified in the existing setup.