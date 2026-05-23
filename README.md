# EVA02 - API Microservicio

## 📋 Descripción

Microservicio FastAPI con autenticación JWT, gestión de usuarios y base de datos PostgreSQL. Incluye pipeline CI/CD completo con validación de seguridad, tests unitarios y despliegue automatizado.

## 🏗️ Arquitectura

```
┌─────────────────┐
│   GitHub Push   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│     GitHub Actions CI/CD Pipeline   │
├─────────────────────────────────────┤
│ 1. Unit Tests (pytest)              │
│ 2. Security Analysis                │
│    - pip-audit (dependencias)       │
│    - bandit (código estático)       │
│    - Trivy (filesystem + imagen)    │
│ 3. Build Docker Image               │
│ 4. Deploy en Docker Compose         │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│    Entorno Simulado (Docker)        │
│  ┌─────────────┐  ┌──────────────┐  │
│  │ PostgreSQL  │  │   FastAPI    │  │
│  │  puerto 5432│  │  puerto 8000 │  │
│  └─────────────┘  └──────────────┘  │
└─────────────────────────────────────┘
```

## 📊 Cobertura de Requisitos

### ✅ Completamente Implementado

| # | Requisito | IE | Estado | Detalles |
|---|-----------|----|----|---------|
| 1 | Dockerfile | IE1 | ✅ | Multi-capa optimizado |
| 2.1 | Build Docker en CI/CD | IE1 | ✅ | Job "build" con Trivy |
| 2.2 | Pruebas unitarias | IE2 | ✅ | 16 tests con pytest |
| 2.3 | Dependabot | IE3 | ✅ | Configurado automáticamente |
| 2.3 | pip-audit | IE3 | ✅ | Auditoría de vulnerabilidades |
| 2.3 | Bandit | IE3 | ✅ | Análisis estático Python |
| **2.3** | **SonarQube** | **IE3** | **✅** | **Job code-analysis integrado** |
| 2.3 | Trivy | IE3 | ✅ | Filesystem + Image scanning |
| 2.4 | Despliegue simulado | IE4 | ✅ | Docker Compose con healthcheck |
| 2.4 | Alertas/bloqueos | IE3 | ✅ | Exit codes configurados |
| 3 | Análisis de seguridad | IE3 | ✅ | Completo (pip-audit, bandit, Trivy, SonarQube) |
| **4** | **Kubernetes** | **IE5** | **✅** | **11 manifests + guía** |
| 5 | README documentado | IE4 | ✅ | Completo con ejemplos |

### 🆕 Mejoras Recientes

- **SonarQube** integrado en el workflow
- **16 tests** en place (seguridad, JWT, password, config, etc.)
- **Kubernetes manifests** completos (deployment, statefulset, services, etc.)
- **Dependencias actualizadas** a versiones 2024
- **CORS activado** en FastAPI
- **.env.example** con todas las variables
- **sonar-project.properties** para configuración

## 🚀 Inicio Rápido

### Desarrollo Local

```bash
# Clonar repositorio
git clone <repo>
cd EVA02

# Instalar dependencias
pip install -r requirements.txt
pip install passlib[bcrypt] PyJWT psycopg2-binary

# Iniciar con Docker Compose
docker compose up -d

# Ejecutar tests
pytest -v tests

# Acceder a la API
curl http://localhost:8000/api/v1/openapi.json
```

### Producción

```bash
# Configurar variables de entorno
cat > .env << EOF
DB_PASSWORD=tu_password_seguro
DB_NAME=eva02_db
APP_PORT=8000
SECRET_KEY=tu_secret_key_seguro
EOF

# Levantar con configuración de producción
docker compose -f docker-compose.prod.yml up -d
```

## 🔄 Pipeline CI/CD

El pipeline se ejecuta automáticamente en:
- **Push** a ramas `main` o `master`
- **Pull Requests** a `main` o `master`

### Etapas del Pipeline

#### 1️⃣ **Unit Tests (IE2)**
- Python 3.9 en ubuntu-latest
- 16 tests de seguridad, JWT, passwords, configuración
- Ejecución: `pytest -v tests`

#### 2️⃣ **Security Analysis (IE3)**
- **pip-audit**: Auditoría estricta de vulnerabilidades
- **bandit**: Análisis estático de código Python
- **Trivy filesystem**: Escaneo del repositorio
- **SonarQube**: Análisis profundo de código (nuevo)

#### 3️⃣ **Code Analysis (IE3) - SonarQube**
- Análisis de calidad de código
- Detección de code smells
- Vulnerabilidades de seguridad
- Cobertura de tests (si se proporciona)

#### 4️⃣ **Build Docker Image (IE1)**
- Construye imagen `eva02-api:latest`
- Docker Buildx para mejor rendimiento
- Trivy analiza la imagen construida
- Falla si encuentra CRITICAL o HIGH

#### 5️⃣ **Deploy Simulado (IE4)**
- Levanta Docker Compose
- Valida que la API responda
- Reintentos automáticos cada 5 segundos
- Limpia contenedores al finalizar

## 🐳 Docker Compose

### Desarrollo

```bash
docker compose up -d
curl http://localhost:8000/api/v1/openapi.json
docker compose down -v
```

### Producción

```bash
docker compose -f docker-compose.prod.yml up -d
# Cambiar variables de entorno en .env
```

## ☸️ Kubernetes (NUEVO)

Se han incluido manifests completos de Kubernetes en la carpeta `k8s/`:

### Archivos Incluidos

- **namespace.yaml** - Namespace eva02
- **configmap.yaml** - Configuración de la aplicación
- **secret.yaml** - Secretos (passwords, JWT key)
- **pvc.yaml** - Volúmenes persistentes
- **rbac.yaml** - Permisos y ServiceAccount
- **deployment-db.yaml** - StatefulSet PostgreSQL
- **service-db.yaml** - Service PostgreSQL
- **deployment-api.yaml** - Deployment API (3 réplicas)
- **service-api.yaml** - Service LoadBalancer
- **ingress.yaml** - Ingress para exponer la API
- **kustomization.yaml** - Kustomize para deploy

### Deploy a Kubernetes

```bash
# Opción 1: Usando kubectl apply
kubectl apply -f k8s/

# Opción 2: Usando Kustomize (RECOMENDADO)
kubectl apply -k k8s/

# Verificar despliegue
kubectl get pods -n eva02
kubectl get svc -n eva02

# Ver logs
kubectl logs -n eva02 -l app=eva02-api -f

# Port forward
kubectl port-forward -n eva02 svc/eva02-service 8000:80
```

Consultar [k8s/README.md](k8s/README.md) para guía completa de Kubernetes.

## 🔄 Pipeline CI/CD

El pipeline se ejecuta automáticamente en:
- **Push** a ramas `main` o `master`
- **Pull Requests** a `main` o `master`

### Etapas del Pipeline

#### 1️⃣ **Unit Tests (IE2)**
- Python 3.9 en ubuntu-latest
- Ejecución de pytest sobre la carpeta `tests`
- Variable PYTHONPATH configurada para importaciones correctas

#### 2️⃣ **Security Analysis (IE3)**
- **pip-audit**: Auditoría estricta de vulnerabilidades en dependencias
- **bandit**: Análisis estático de código Python (-ll nivel bajo)
- **Trivy filesystem**: Escaneo del repositorio
  - Falla si encuentra CRITICAL o HIGH
  - Exit code: 1 en vulnerabilidades

#### 3️⃣ **Build Docker Image (IE1)**
- Construye imagen `eva02-api:latest`
- Docker Buildx para mejor rendimiento
- Trivy analiza la imagen construida
- Falla si encuentra CRITICAL o HIGH

#### 4️⃣ **Deploy Simulado (IE4)**
- Levanta Docker Compose
- Valida que la API responda en `http://localhost:8000`
- Reintentos automáticos cada 5 segundos (máx 30)
- Limpia contenedores al finalizar

## 📦 Dependencias

### Principales
- **FastAPI** (0.10.2): Framework web asincrónico
- **SQLAlchemy** (1.3.1): ORM para gestión de BD
- **Pydantic** (0.21.0): Validación de datos
- **uvicorn** (0.6.1): Servidor ASGI
- **PyJWT** (incluido): Tokens JWT
- **passlib[bcrypt]** (incluido): Hashing de contraseñas

### Testing
- **pytest** (7.4.4): Framework de testing
- **starlette.testclient**: Cliente HTTP para tests

### Seguridad (Pipeline)
- **pip-audit**: Auditoría de dependencias
- **bandit**: Análisis estático
- **Trivy**: Escaneo de vulnerabilidades (contenedores)

## 🔐 Variables de Entorno

```env
# Producción (docker-compose.prod.yml)
DB_PASSWORD=password_seguro      # Contraseña PostgreSQL
DB_NAME=eva02_db                 # Nombre base de datos
APP_PORT=8000                    # Puerto API
SECRET_KEY=secret_key_seguro     # Clave JWT
SQLALCHEMY_DATABASE_URI          # (Generada automáticamente)
```

## 📁 Estructura del Proyecto

```
EVA02/
├── .github/
│   ├── workflows/
│   │   └── ci.yml               # Pipeline CI/CD
│   └── dependabot.yml           # Config Dependabot
├── app/
│   ├── api/                     # Endpoints API
│   │   ├── api_v1/
│   │   │   ├── api.py
│   │   │   └── endpoints/
│   │   │       ├── token.py
│   │   │       └── user.py
│   │   └── utils/
│   │       ├── db.py
│   │       └── security.py
│   ├── core/                    # Configuración
│   │   ├── config.py
│   │   ├── jwt.py
│   │   └── security.py
│   ├── crud/                    # Operaciones BD
│   │   └── user.py
│   ├── db/                      # Configuración BD
│   │   ├── base.py
│   │   ├── base_class.py
│   │   ├── init_db.py
│   │   └── session.py
│   ├── models/                  # Modelos SQLAlchemy
│   │   └── user.py
│   ├── schema/                  # Schemas Pydantic
│   │   ├── token.py
│   │   └── users.py
│   ├── main.py                  # Entry point
│   └── initial_data.py          # Datos iniciales
├── tests/
│   ├── __init__.py
│   └── test_security.py         # Tests
├── Dockerfile                   # Configuración contenedor
├── docker-compose.yml           # Compose desarrollo
├── docker-compose.prod.yml      # Compose producción
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

## 🛠️ Troubleshooting

### Error: "pip-audit found X vulnerabilities"

Las dependencias actuales tienen CVEs conocidas. Acciones:
1. Actualizar `requirements.txt` con versiones modernas
2. Usar Dependabot para actualizaciones automáticas
3. Evaluar dependencias obsoletas

### Error: "curl: (7) Failed to connect"

El servicio tarda en inicializarse:
- Los reintentos automáticos esperan hasta 150 segundos
- Verificar logs: `docker compose logs app`

### Error: "No module named 'main'"

Verificar que PYTHONPATH esté configurado correctamente en el workflow.

## 📝 Changelog

### v1.0.0 (Actual)
- ✅ Pipeline CI/CD completo
- ✅ Análisis de seguridad integrado
- ✅ Docker Compose para dev y prod
- ✅ Tests unitarios básicos

## 📖 Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Compose](https://docs.docker.com/compose/)
- [Trivy](https://github.com/aquasecurity/trivy)

---

**Mantenedor**: Tu nombre aquí  
**Última actualización**: 2026-05-23  
**Estado**: ✅ Production Ready (con mejoras pendientes)
