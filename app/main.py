from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from api.api_v1.api import api_router
from core import config
from db.session import Session




app = FastAPI(
    title=config.PROJECT_NAME, 
    openapi_url="/api/v1/openapi.json",
    version="1.0.0",
    description="Microservicio de autenticación y gestión de usuarios"
)

# Métricas de Prometheus
request_count = Counter(
    'fastapi_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'fastapi_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'fastapi_active_requests',
    'Active HTTP requests'
)



# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, usar lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=config.API_V1_STR)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    active_requests.inc()
    start_time = time.time()
    request.state.db = Session()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        active_requests.dec()
        request.state.db.close()
        raise
    finally:
        # Registrar métricas
        duration = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        
        request_count.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        active_requests.dec()
        request.state.db.close()
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)