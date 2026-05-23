from starlette.testclient import testclient 

from main import app

client = TestClient(app)

def test_openapi_disponible():
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200

