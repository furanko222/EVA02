# Runbook: Despliegue de EVA02

Este runbook describe pasos seguros para desplegar la API y cómo hacer rollback.

## Pre-requisitos
- Acceso al registry (si aplica) y credenciales en `secrets` de GitHub
- Acceso al clúster Kubernetes o a la máquina con `docker compose`
- Tener imágenes construidas y etiquetadas (tag semántico)

## Despliegue con Docker Compose (entorno de pruebas)

1. Construir imagen localmente:

```bash
docker build -t <registry>/eva02-api:<tag> .
```

2. (Opcional) Push a registry privado:

```bash
docker push <registry>/eva02-api:<tag>
```

3. Actualizar `.env` con variables necesarias (usar secrets en producción).

4. Levantar servicios:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

5. Verificar disponibilidad:

```bash
curl -f http://localhost:8000/api/v1/openapi.json || (docker compose logs && exit 1)
```

6. Si falla, ver logs de servicios y recuperar estado anterior:

```bash
docker compose logs --tail=200
docker compose down -v
docker compose up -d --no-build
```

## Despliegue a Kubernetes

1. Actualizar `k8s/` con el nuevo tag (ej. `image: <registry>/eva02-api:<tag>`).
2. Aplicar recursos con kustomize o kubectl:

```bash
kubectl apply -k k8s/ -n eva02
```

3. Verificar pods y readiness/liveness:

```bash
kubectl rollout status deployment/eva02-api -n eva02
kubectl get pods -n eva02 -o wide
kubectl logs -n eva02 -l app=eva02-api --tail=200
```

4. Rollback (si el rollout falla):

```bash
kubectl rollout undo deployment/eva02-api -n eva02
```

## Healthchecks y monitoreo
- Revisar `/metrics` y que Prometheus scrapee la instancia.
- Revisar dashboards de Grafana y alertas.

## Post-despliegue
- Ejecutar tests de integración básicos contra la API.
- Confirmar no hay errores críticos en logs y que las métricas son estables.

## Notas
- No subir secretos al repo. Usar `kubectl create secret` o la UI del proveedor.
- Documentar cualquier cambio de DB/migraciones en `CHANGELOG.md`.
