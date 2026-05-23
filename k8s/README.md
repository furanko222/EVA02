# Kubernetes Deployment Guide - EVA02 API

## 📋 Requisitos Previos

1. **Cluster Kubernetes** (minikube, EKS, AKS, GKE, etc.)
2. **kubectl** instalado y configurado
3. **Imagen Docker** construida: `eva02-api:latest`
4. **Kustomize** (opcional, si usas Kustomization)

## 🚀 Deploying a Kubernetes

### 1. Verificar conexión al cluster

```bash
kubectl cluster-info
kubectl get nodes
```

### 2. Crear el namespace y recursos

```bash
# Opción A: Usando kubectl apply
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/service-db.yaml
kubectl apply -f k8s/deployment-db.yaml
kubectl apply -f k8s/service-api.yaml
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/ingress.yaml

# Opción B: Usando Kustomize (RECOMENDADO)
kubectl apply -k k8s/
```

### 3. Verificar el despliegue

```bash
# Verificar namespace
kubectl get namespace eva02

# Verificar pods
kubectl get pods -n eva02
kubectl get pods -n eva02 -w  # Watch en tiempo real

# Verificar servicios
kubectl get svc -n eva02

# Verificar despliegues
kubectl get deployments -n eva02
kubectl get statefulsets -n eva02
```

### 4. Acceder a los logs

```bash
# Logs de la API
kubectl logs -n eva02 -l app=eva02-api -f

# Logs de PostgreSQL
kubectl logs -n eva02 -l app=postgres -f

# Logs de un pod específico
kubectl logs -n eva02 <pod-name>

# Logs anteriores (si el pod fue reiniciado)
kubectl logs -n eva02 <pod-name> --previous
```

### 5. Port Forwarding (Desarrollo Local)

```bash
# API
kubectl port-forward -n eva02 svc/eva02-service 8000:80

# PostgreSQL
kubectl port-forward -n eva02 svc/postgres-service 5432:5432

# Acceder:
# API: http://localhost:8000
# DB: postgresql://postgres:pass@localhost:5432/eva02_db
```

### 6. Ejecutar comandos dentro de un pod

```bash
# Bash en la API
kubectl exec -it -n eva02 <pod-name> -- /bin/bash

# Ejecutar pytest en la API
kubectl exec -n eva02 <pod-name> -- python -m pytest /code/tests

# Conectar a PostgreSQL
kubectl exec -it -n eva02 postgres-db-0 -- psql -U postgres -d eva02_db
```

## 🔧 Configuración en Producción

### Variables de Entorno a Cambiar

1. **Secrets** (`k8s/secret.yaml`):
   - `SECRET_KEY`: Generar con `openssl rand -hex 32`
   - `DB_PASSWORD`: Cambiar a password seguro
   - `FIRST_SUPERUSER_PASSWORD`: Cambiar contraseña

2. **ConfigMap** (`k8s/configmap.yaml`):
   - `DEBUG`: Cambiar de `false` a `true` si es necesario
   - `LOG_LEVEL`: Ajustar según necesidad

3. **Ingress** (`k8s/ingress.yaml`):
   - Cambiar `api.example.com` a tu dominio real
   - Configurar certificado TLS
   - Cambiar `clusterissuer` si es necesario

4. **Deployment** (`k8s/deployment-api.yaml`):
   - `replicas`: Aumentar según carga esperada
   - `resources`: Ajustar requests/limits según máquina
   - `imagePullPolicy`: Cambiar a `Always` en producción

5. **Almacenamiento** (`k8s/pvc.yaml`):
   - `storageClassName`: Cambiar según tu proveedor (EBS, AzureDisk, etc.)
   - `storage`: Aumentar tamaño si es necesario

### Variables de Entorno Importantes

```bash
# Encodear valores en base64 para el Secret
echo -n "my-secret-value" | base64
# Resultado: bXktc2VjcmV0LXZhbHVl

# Luego copiar en k8s/secret.yaml
```

## 📊 Escalabilidad

### Aumentar réplicas de la API

```bash
# Editar el deployment
kubectl edit deployment eva02-api -n eva02

# O cambiar directamente
kubectl scale deployment eva02-api -n eva02 --replicas=5
```

### Usar Horizontal Pod Autoscaler (HPA)

```bash
kubectl autoscale deployment eva02-api -n eva02 --min=2 --max=10 --cpu-percent=80
```

## 🔒 Seguridad

### Verificar políticas de seguridad

```bash
# Verificar contexto de seguridad
kubectl get pods -n eva02 -o jsonpath='{.items[*].spec.securityContext}'

# Verificar RBAC
kubectl get rolebindings -n eva02
kubectl get roles -n eva02
```

### Actualizaciones seguras

Las configuraciones incluyen:
- ✅ Security Context (runAsNonRoot)
- ✅ Resource Limits
- ✅ Liveness/Readiness Probes
- ✅ RBAC configurado
- ✅ Pod Anti-affinity (distribuir pods)

## 🧹 Limpiar recursos

```bash
# Eliminar todos los recursos del namespace
kubectl delete namespace eva02

# O si quieres mantener el namespace:
kubectl delete -k k8s/ -n eva02
```

## 🐛 Troubleshooting

### Pod no inicia

```bash
kubectl describe pod -n eva02 <pod-name>
kubectl logs -n eva02 <pod-name>
```

### Base de datos no accesible

```bash
# Verificar que el StatefulSet está listo
kubectl get statefulsets -n eva02

# Verificar conexión a PostgreSQL
kubectl exec -it -n eva02 <api-pod> -- \
  python -c "import psycopg2; print('Conexión OK')"
```

### Ingress no funciona

```bash
# Verificar ingress
kubectl get ingress -n eva02
kubectl describe ingress eva02-ingress -n eva02

# Verificar resolver DNS
nslookup api.example.com
```

## 📚 Archivos en k8s/

| Archivo | Propósito |
|---------|-----------|
| `namespace.yaml` | Namespace eva02 |
| `configmap.yaml` | Configuración de app |
| `secret.yaml` | Secretos (passwords, keys) |
| `pvc.yaml` | Volúmenes persistentes |
| `rbac.yaml` | Permisos (ServiceAccount, Roles) |
| `deployment-db.yaml` | StatefulSet PostgreSQL |
| `service-db.yaml` | Service PostgreSQL |
| `deployment-api.yaml` | Deployment API |
| `service-api.yaml` | Service API |
| `ingress.yaml` | Ingress para exponer la API |
| `kustomization.yaml` | Kustomization para deploy |

## 🔗 Referencias

- [Kubernetes Docs](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kustomize](https://kustomize.io/)
