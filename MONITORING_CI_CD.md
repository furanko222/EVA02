# Monitoreo, Dashboards y Políticas de Cumplimiento - EVA02

## 📌 Resumen Ejecutivo

Este documento describe la implementación completa de:
- **IE1**: Herramientas de monitoreo (Prometheus + Grafana)
- **IE2**: Despliegue en Docker Compose
- **IE3**: Dashboard con métricas clave
- **IE4**: Políticas de cumplimiento en CI/CD (SonarQube, pip-audit, Bandit, Trivy)
- **IE5**: Documentación de integración
- **IE6**: Verificación de detención de pipeline en fallos críticos

---

## IE1: Herramientas de Monitoreo

### Prometheus

**Descripción**: Sistema de monitoreo que recolecta métricas en tiempo real del microservicio.

**Configuración**: `monitoring/prometheus.yml`

**Acceso**: http://localhost:9090

**Funcionalidades**:
- Recolecta métricas cada 10 segundos del endpoint `/metrics` de FastAPI
- Almacena datos en serie temporal (TSDB)
- Permite consultas PromQL
- Retención de 15 días de datos

**Métricas recolectadas**:
- `fastapi_requests_total`: Total de peticiones HTTP por método, endpoint y código de estado
- `fastapi_request_duration_seconds`: Histograma de duración de peticiones
- `fastapi_active_requests`: Gauge de peticiones activas en tiempo real

### Grafana

**Descripción**: Plataforma de visualización de métricas con dashboards interactivos.

**Acceso**: http://localhost:3000

**Credenciales de inicio**:
- Usuario: `admin`
- Contraseña: `admin`

**Dashboard Automático**: "FastAPI Metrics - EVA02"
- Visualiza las 4 métricas principales
- Se actualiza cada 30 segundos
- Incluye gráficos, estadísticas y mapas de calor

---

## IE2: Despliegue en Docker Compose

### Arquitectura

```
┌─────────────────────────────────────────┐
│        Docker Compose Network            │
│           (eva02-net)                    │
│                                          │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │  PostgreSQL  │  │  FastAPI App     │ │
│  │  :5432       │  │  :8000           │ │
│  │  (db)        │  │  (/metrics)      │ │
│  └──────────────┘  └──────────────────┘ │
│         ▲                    ▲           │
│         │ Depende de         │ Expone   │
│         │ healthcheck        │ métricas  │
│         │                    │           │
│  ┌──────────────┐  ┌──────────────────┐ │
│  │ Prometheus   │  │  Grafana         │ │
│  │  :9090       │  │  :3000           │ │
│  │ (scrape)     │  │ (visualiza)      │ │
│  └──────────────┘  └──────────────────┘ │
│         ▲                    ▲           │
│         │ Lee config         │ Lee      │
│         │ prometheus.yml     │ datasources
│         │                    │           │
└─────────────────────────────────────────┘
```

### Servicios

#### 1. **db** (PostgreSQL)
```yaml
- Puerto: 5432
- Imagen: postgres:15.1
- Volumen: ./data/postgres
- Healthcheck: pg_isready
```

#### 2. **app** (FastAPI)
```yaml
- Puerto: 8000
- Construcción: Dockerfile local
- Depende de: db (healthcheck)
- Expone: /metrics en puerto 8000
- Healthcheck: curl /api/v1/openapi.json
```

#### 3. **prometheus**
```yaml
- Puerto: 9090
- Imagen: prom/prometheus:latest
- Configuración: ./monitoring/prometheus.yml
- Volumen persistente: prometheus_data
- Depende de: app
```

#### 4. **grafana**
```yaml
- Puerto: 3000
- Imagen: grafana/grafana:latest
- Contraseña admin: admin
- Volumen persistente: grafana_data
- Depende de: prometheus
```

### Levantar el Stack

```bash
# Crear carpeta de datos
mkdir -p data/postgres

# Levantar servicios
docker compose up -d

# Ver logs
docker compose logs -f app

# Esperar a que la app esté lista (30 segundos aprox)
curl http://localhost:8000/api/v1/openapi.json

# Bajar servicios
docker compose down -v
```

---

## IE3: Dashboard con Métricas Clave

### Ubicación

Archivo: `monitoring/grafana/provisioning/dashboards/dashboard.json`

### Visualizaciones Incluidas

#### Panel 1: Request Rate (Gráfico de línea)
- **Métrica**: `rate(fastapi_requests_total[1m])`
- **Visualiza**: Peticiones por segundo
- **Eje X**: Tiempo
- **Eje Y**: Requests/sec
- **Uso**: Detectar picos de tráfico

#### Panel 2: Response Time p95 (Gráfico de línea)
- **Métrica**: `histogram_quantile(0.95, rate(fastapi_request_duration_seconds_bucket[5m]))`
- **Visualiza**: Percentil 95 de latencia
- **Unidad**: Milisegundos
- **Uso**: Monitorear performance

#### Panel 3: Active Requests (Estadística)
- **Métrica**: `fastapi_active_requests`
- **Visualiza**: Valor actual de peticiones activas
- **Tipo**: Número grande
- **Uso**: Detectar congestión

#### Panel 4: Total Requests by Status (Gráfico de pastel)
- **Métrica**: `fastapi_requests_total`
- **Etiquetado por**: status_code (200, 401, 500, etc.)
- **Uso**: Identificar errores

#### Panel 5: Response Time Distribution (Mapa de calor)
- **Métrica**: `rate(fastapi_request_duration_seconds_bucket[5m])`
- **Visualiza**: Distribución de latencias
- **Uso**: Análisis detallado de performance

### Acceso al Dashboard

1. Abre http://localhost:3000
2. Login: admin / admin
3. Ve a "Dashboards" → "Browse"
4. Selecciona "FastAPI Metrics - EVA02"
5. Genera tráfico:
   ```bash
   # En otra terminal
   for i in {1..100}; do
     curl http://localhost:8000/api/v1/openapi.json &
   done
   ```
6. Observa en tiempo real cómo las métricas se actualizan

---

## IE4: Políticas de Cumplimiento en CI/CD

### Pipeline Workflow

```
GitHub Push (main/master)
    ↓
┌─────────────────────────────────────┐
│  Job: test                          │
│  - pytest (coverage >= 40%)         │
│  - ❌ Si falla → STOP PIPELINE      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Job: security                      │
│  - pip-audit (dependencias)         │
│  - bandit (código Python)           │
│  - trivy fs (filesystem)            │
│  - ❌ Si CRITICAL/HIGH → STOP       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Job: code-analysis                 │
│  - flake8 (sintaxis)                │
│  - SonarCloud (calidad)             │
│  - ❌ Si SonarCloud falla → STOP    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Job: docker-lint                   │
│  - hadolint (Dockerfile)            │
│  - ❌ Si warnings → STOP             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Job: build                         │
│  - docker build & push              │
│  - trivy image scan                 │
│  - ❌ Si vulnerabilidades → STOP    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Job: deploy (simulado)             │
│  - docker compose up -d             │
│  - curl health check                │
│  - ✅ SUCCESS si todo ok            │
└─────────────────────────────────────┘
```

### Herramientas de Análisis

| Herramienta | Tipo | Qué Detecta | Stop en |
|-------------|------|-------------|---------|
| **pytest** | Testing | Tests fallidos, cobertura baja | Cobertura < 40% |
| **pip-audit** | SCA | Dependencias con CVEs conocidos | CVE detectado |
| **bandit** | SAST | Issues de seguridad en código | Security level LL |
| **trivy fs** | SAST | Vulnerabilidades en archivos | Severidad CRITICAL/HIGH |
| **flake8** | Linting | Errores de sintaxis Python | Error tipo E9, F63, F7, F82 |
| **SonarCloud** | Code Quality | Coverage, duplicación, bugs | Quality Gate fallido |
| **hadolint** | Container Lint | Problemas en Dockerfile | Warning level |
| **trivy image** | Container Scan | Vulnerabilidades en imagen | Severidad CRITICAL/HIGH |

### Cambios Realizados para IE6

**Antes**:
```yaml
- name: SonarCloud
  continue-on-error: true  ❌ Permitía continuar aunque falle
```

**Después**:
```yaml
- name: SonarCloud
  continue-on-error: false  ✅ Detiene pipeline si falla
```

### Job Dependency Chain

```yaml
build:
  needs: [test, security, code-analysis, docker-lint]
```

Si **cualquiera** falla → El job `build` nunca se ejecuta → **Pipeline se detiene** (IE6)

---

## IE5: Documentación de Integración

### Flujo Técnico Completo

#### 1. **Desarrollo Local**
```bash
# El desarrollador modifica código
git add .
git commit -m "Feature: agregar endpoint X"
git push origin main
```

#### 2. **GitHub Actions Dispara CI**
```
Trigger: on: push to main
```

#### 3. **Ejecución de Tests**
```bash
pytest -v tests --cov=app --cov-fail-under=40
# Si coverage < 40% → JOB FAIL → PIPELINE STOP
```

#### 4. **Análisis de Seguridad**
```bash
pip-audit -r requirements.txt
# Si CVE encontrado → JOB FAIL → PIPELINE STOP

bandit -r app -ll
# Si security issue LL → JOB FAIL → PIPELINE STOP

trivy fs . --severity CRITICAL,HIGH
# Si vulnerabilidad → JOB FAIL → PIPELINE STOP
```

#### 5. **Análisis de Calidad**
```bash
flake8 app --select=E9,F63,F7,F82
# Si errores → JOB FAIL → PIPELINE STOP

sonar-scanner \
  -Dsonar.projectKey=eva02-api \
  -Dsonar.sources=app
# Si Quality Gate fallido → JOB FAIL → PIPELINE STOP (continue-on-error: false)
```

#### 6. **Build Docker Image**
```bash
# Solo si tests, security, code-analysis, docker-lint TODOS pasaron
docker build -t eva02-api:latest .
docker scan eva02-api:latest
# Si vulnerabilidades CRITICAL/HIGH → JOB FAIL
```

#### 7. **Deploy Simulado**
```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/openapi.json
# Si falla → JOB FAIL
docker compose down -v
```

#### 8. **Prometheus Recolecta Métricas**
```
A los 10 segundos:
Prometheus scrape http://app:8000/metrics
↓
Almacena:
- fastapi_requests_total
- fastapi_request_duration_seconds
- fastapi_active_requests
```

#### 9. **Grafana Visualiza**
```
Grafana lee datos de Prometheus cada 30 segundos
↓
Dashboard "FastAPI Metrics - EVA02" se actualiza
↓
Usuario ve gráficos en tiempo real
```

### Decisiones Técnicas

| Decisión | Opción Elegida | Justificación |
|----------|----------------|--------------|
| Stack de Monitoreo | Prometheus + Grafana | Open source, estándar, sin costo |
| Librería de Métricas | prometheus-client | Oficial, integración simple con FastAPI |
| Orquestación | Docker Compose | Simula producción, fácil de entender |
| SCA | pip-audit | Detecta CVEs conocidos en PyPI |
| SAST | Bandit | Especializado en Python |
| Linting | Flake8 | Estándar Python, rápido |
| Container Scanning | Trivy | Detecta vulnerabilidades en capas |
| Quality Gate | SonarCloud | Integración con GitHub, análisis profundo |
| Detención de Pipeline | continue-on-error: false | Detiene si falla, máxima seguridad |

---

## IE6: Verificación de Detención de Pipeline

### Prueba 1: Fallo de Coverage

**Objetivo**: Verificar que pipeline se detiene si coverage < 40%

**Pasos**:
1. Edita `tests/test_security.py` y deja un test comentado
2. O elimina la mayoría de tests
3. Haz push:
   ```bash
   git add .
   git commit -m "TEST: reduce coverage"
   git push origin main
   ```

**Resultado esperado**:
- ❌ Job `test` falla
- ⏸️ Job `security` no se ejecuta (falta depender de test)
- ⏸️ Job `build` no se ejecuta (needs: test)
- ⏸️ Job `deploy` no se ejecuta

**En GitHub Actions**:
```
✅ test
  FAIL: Coverage 35% < 40%
⏹️ security (waiting for test)
⏹️ code-analysis (waiting for test)
⏹️ build (needs: [test, ...])
⏹️ deploy (needs: [build])
```

### Prueba 2: Fallo de Vulnerabilidad en Dependencias

**Objetivo**: Verificar que pipeline detiene en CVE

**Pasos**:
1. En `requirements.txt`, añade una versión vulnerable:
   ```
   # Versión vulnerable de requests
   requests==2.25.0
   ```
2. Haz push:
   ```bash
   git add requirements.txt
   git commit -m "TEST: add vulnerable dependency"
   git push origin main
   ```

**Resultado esperado**:
- ✅ Job `test` pasa
- ❌ Job `security` falla (pip-audit detecta CVE)
- ⏸️ Job `build` no se ejecuta

**Output en GitHub**:
```
✅ test
❌ security
  FAIL: pip-audit detected CVE
    requests 2.25.0: CVE-2023-32681
⏹️ code-analysis
⏹️ build
```

### Prueba 3: Fallo de Seguridad en Código

**Objetivo**: Verificar que pipeline detiene en issue SAST

**Pasos**:
1. En `app/api/api_v1/endpoints/user.py`, añade código vulnerable:
   ```python
   import pickle
   
   @router.post("/load")
   def load_data(data: str):
       return pickle.loads(data)  # ❌ Security issue: pickle injection
   ```
2. Haz push

**Resultado esperado**:
- ✅ Job `test`
- ❌ Job `security` falla (Bandit detecta pickle.loads)

**Mensaje**:
```
WARN: Probable use of pickle.loads
      Issue: Pickle can execute arbitrary code
```

### Prueba 4: Fallo de SonarCloud Quality Gate

**Objetivo**: Verificar que SonarCloud detiene pipeline

**Requisitos**: Configurar `SONAR_TOKEN` en GitHub Secrets

**Pasos**:
1. Ve a [SonarCloud](https://sonarcloud.io) → Sign in con GitHub
2. Autoriza acceso al repo
3. Copia el `SONAR_TOKEN`
4. En GitHub → Settings → Secrets → Agrega `SONAR_TOKEN`
5. Haz un push a main

**Resultado esperado**:
- ✅ test
- ✅ security
- ⚠️ code-analysis
  - ✅ flake8
  - SonarCloud análisis...
  - Si Quality Gate falla → ❌ Job fail

### Prueba 5: Fallo de Build

**Objetivo**: Verificar que pipeline detiene si Docker build falla

**Pasos**:
1. En `Dockerfile`, crea un error:
   ```dockerfile
   FROM python:3.9
   RUN invalid-command-here
   ```
2. Haz push

**Resultado esperado**:
- ✅ test, security, code-analysis, docker-lint
- ❌ Job `build` falla (Docker build error)
- ⏹️ Job `deploy` no se ejecuta

---

## Cómo Usar en Producción

### Requisitos

- Docker Desktop o Docker Engine 20.10+
- docker-compose 2.0+
- Git

### Setup Inicial

```bash
# Clonar repo
git clone <repo-url>
cd EVA02

# Crear carpeta de datos
mkdir -p data/postgres

# Variables de entorno (opcional)
cat > .env << EOF
POSTGRES_PASSWORD=pass
POSTGRES_DB=test_db
SECRET_KEY=your-secret-key
EOF

# Levantar stack
docker compose up -d --build

# Esperar a que levante (30-60 segundos)
sleep 60

# Verificar que funciona
curl http://localhost:8000/api/v1/openapi.json
curl http://localhost:9090
curl http://localhost:3000
```

### Acceso a Servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| FastAPI | http://localhost:8000 | - |
| Swagger UI | http://localhost:8000/docs | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin / admin |
| PostgreSQL | localhost:5432 | postgres / pass |

### Generar Tráfico para Pruebas

```bash
# Terminal 1: Ver logs en tiempo real
docker compose logs -f app

# Terminal 2: Generar peticiones
bash -c 'for i in {1..100}; do
  curl -s http://localhost:8000/api/v1/openapi.json > /dev/null &
done; wait'

# Terminal 3: Ver métricas en Grafana
# Abre http://localhost:3000 → Dashboards → FastAPI Metrics - EVA02
```

### Troubleshooting

#### Prometheus no recolecta métricas

```bash
# Verificar que FastAPI expone métricas
curl http://localhost:8000/metrics

# Verificar logs de Prometheus
docker compose logs prometheus

# Verificar config de Prometheus
docker compose exec prometheus cat /etc/prometheus/prometheus.yml
```

#### Grafana sin datasource

```bash
# Verificar archivo provisioning
cat monitoring/grafana/provisioning/datasources/prometheus.yml

# Reiniciar Grafana
docker compose restart grafana
```

#### Pipeline de GitHub falla aleatoriamente

```bash
# Revisar logs de GitHub Actions
# GitHub → Actions → Workflow run → Logs

# Verificar que tests son deterministas (no usan timestamps)
pytest tests/ -v --tb=short
```

---

## Checklist de Implementación

- [x] IE1: Prometheus configurado (`monitoring/prometheus.yml`)
- [x] IE1: prometheus-client en requirements.txt
- [x] IE2: Docker Compose con 4 servicios (db, app, prometheus, grafana)
- [x] IE2: Volúmenes persistentes para Prometheus y Grafana
- [x] IE3: Endpoint `/metrics` en FastAPI
- [x] IE3: Métricas: requests_total, request_duration, active_requests
- [x] IE3: Dashboard Grafana con 5 paneles
- [x] IE3: Datasource provisioning automático
- [x] IE4: pip-audit en pipeline
- [x] IE4: Bandit en pipeline
- [x] IE4: Trivy filesystem + image
- [x] IE4: SonarCloud integrado
- [x] IE4: Flake8 para linting
- [x] IE5: Documentación completa
- [x] IE6: SonarCloud con `continue-on-error: false`
- [x] IE6: Job dependency chain (build needs [test, security, code-analysis, docker-lint])

---

## Referencias

- [Prometheus Docs](https://prometheus.io/docs/)
- [Grafana Docs](https://grafana.com/docs/)
- [prometheus-client Python](https://github.com/prometheus/client_python)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Trivy Scanner](https://aquasecurity.github.io/trivy/)
- [SonarCloud](https://sonarcloud.io/)

---

**Última actualización**: 2026-06-23

**Versión**: 1.0

**Responsable**: Equipo de Desarrollo EVA02