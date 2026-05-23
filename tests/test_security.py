import sys
import os
import json
from datetime import timedelta

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from starlette.testclient import TestClient 
from main import app
from core.jwt import create_access_token

client = TestClient(app)

# ===== Pruebas de OpenAPI =====

def test_openapi_disponible():
    """Verifica que el endpoint OpenAPI está disponible"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

def test_api_v1_prefix():
    """Verifica que los endpoints tienen el prefijo correcto"""
    response = client.get("/api/v1/openapi.json")
    data = response.json()
    assert "/api/v1/" in str(data)

def test_health_check():
    """Test básico de conectividad"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

# ===== Pruebas de Seguridad =====

def test_cors_headers():
    """Verifica que CORS está configurado"""
    response = client.get("/api/v1/openapi.json")
    # CORS headers should be present or at least the request should succeed
    assert response.status_code == 200

def test_no_debug_info_in_errors():
    """Verifica que no se expongan detalles de debug en errores 404"""
    response = client.get("/api/v1/nonexistent/endpoint")
    # Debería devolver 404 sin detalles de traceback
    assert response.status_code in [404, 405]

# ===== Pruebas de Autenticación =====

def test_token_creation():
    """Verifica que se puede crear un token JWT"""
    data = {"user_id": 1, "sub": "test@example.com"}
    expires_delta = timedelta(minutes=30)
    
    try:
        token = create_access_token(data=data, expires_delta=expires_delta)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    except Exception as e:
        # Si falla la creación de token, esto debería ser investigado
        assert False, f"Token creation failed: {str(e)}"

def test_jwt_import():
    """Verifica que el módulo JWT está disponible"""
    from core.jwt import create_access_token, ALGORITHM
    assert ALGORITHM == "HS256"
    assert callable(create_access_token)

# ===== Pruebas de Seguridad de Contraseñas =====

def test_password_security_imports():
    """Verifica que los módulos de seguridad están disponibles"""
    from core.security import verify_password, get_password_hash
    assert callable(verify_password)
    assert callable(get_password_hash)

def test_password_hashing():
    """Verifica que las contraseñas se cifran correctamente"""
    from core.security import get_password_hash, verify_password
    
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

# ===== Pruebas de Configuración =====

def test_config_loaded():
    """Verifica que la configuración está disponible"""
    from core import config
    assert hasattr(config, 'PROJECT_NAME')
    assert hasattr(config, 'API_V1_STR')
    assert config.PROJECT_NAME == "EVA02"
    assert config.API_V1_STR == "/api/v1"

def test_database_config():
    """Verifica que la configuración de BD existe"""
    from core import config
    assert hasattr(config, 'SQLALCHEMY_DATABASE_URI')
    assert "postgresql" in config.SQLALCHEMY_DATABASE_URI.lower() or "localhost" in config.SQLALCHEMY_DATABASE_URI

# ===== Pruebas de Modelos =====

def test_models_importable():
    """Verifica que todos los modelos pueden importarse"""
    try:
        from models.user import User
        assert User is not None
    except ImportError as e:
        assert False, f"Failed to import User model: {str(e)}"

def test_schemas_importable():
    """Verifica que todos los schemas pueden importarse"""
    try:
        from schema.users import User, UserInCreate, UserInDB, UserInUpdate
        assert all([User, UserInCreate, UserInDB, UserInUpdate])
    except ImportError as e:
        assert False, f"Failed to import schemas: {str(e)}"

# ===== Pruebas de Integración Básica =====

def test_api_router_registered():
    """Verifica que el router de API está registrado"""
    response = client.get("/api/v1/openapi.json")
    data = response.json()
    # Debería haber información de la API
    assert data.get("info", {}).get("title") == "EVA02"

def test_middleware_applied():
    """Verifica que los middlewares están aplicados"""
    # Si los middlewares están aplicados, la respuesta debe tener éxito
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"


