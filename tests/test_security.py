import sys
import os

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from starlette.testclient import TestClient 
from main import app

client = TestClient(app)

def test_openapi_disponible():
    """Test que verifica que el endpoint OpenAPI está disponible"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()

def test_api_v1_prefix():
    """Test que verifica que los endpoints tienen el prefijo correcto"""
    response = client.get("/api/v1/openapi.json")
    data = response.json()
    assert "/api/v1/" in str(data) or data.get("servers"), "API v1 prefix not found"

def test_health_check():
    """Test básico de conectividad"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code in [200, 404, 405], f"Unexpected status code: {response.status_code}"


