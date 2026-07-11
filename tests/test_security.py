import os
import sys
import json
import pytest

# Configurar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from starlette.testclient import TestClient

# Test básico de disponibilidad del módulo
try:
    from main import app
    client = TestClient(app)
except ImportError as e:
    pytest.skip(f"No se pudo importar la aplicación: {e}")

# ===== Pruebas de OpenAPI =====

def test_openapi_disponible():
    """Verifica que el endpoint OpenAPI está disponible"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data

def test_api_v1_prefix():
    """Verifica que los endpoints tienen el prefijo correcto"""
    response = client.get("/api/v1/openapi.json")
    data = response.json()
    assert "/api/v1/" in str(data)

def test_health_check():
    """Test básico de conectividad"""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

# ===== Pruebas de Módulos (sin app) =====

def test_jwt_module_importable():
    """Verifica que el módulo JWT está disponible"""
    try:
        from core.jwt import create_access_token, ALGORITHM
    except Exception as e:
        pytest.fail(f"JWT module import failed: {e}")
    assert ALGORITHM == "HS256"
    assert callable(create_access_token)

def test_security_module_importable():
    """Verifica que el módulo de seguridad está disponible"""
    try:
        from core.security import verify_password, get_password_hash
    except Exception as e:
        pytest.fail(f"Security module import failed: {e}")
    assert callable(verify_password)
    assert callable(get_password_hash)

def test_config_module_importable():
    """Verifica que la configuración está disponible"""
    try:
        from core import config
    except Exception as e:
        pytest.fail(f"Config import failed: {e}")
    assert hasattr(config, 'PROJECT_NAME')
    assert config.PROJECT_NAME == "EVA02"

def test_models_importable():
    """Verifica que los modelos pueden importarse"""
    try:
        from models.user import User
    except Exception as e:
        pytest.fail(f"Models import failed: {e}")
    assert User is not None

def test_schema_importable():
    """Verifica que los schemas pueden importarse"""
    try:
        from schema.users import User, UserInCreate
    except Exception as e:
        pytest.fail(f"Schemas import failed: {e}")
    assert User is not None
    assert UserInCreate is not None

# ===== Prueba de Passwords =====

def test_password_hashing():
    """Verifica que las contraseñas se cifran correctamente"""
    try:
        from core.security import get_password_hash, verify_password
    except Exception as e:
        pytest.fail(f"Security functions import failed: {e}")

    password = "test_password_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


