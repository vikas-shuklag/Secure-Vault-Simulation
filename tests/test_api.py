from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_get_404_on_root():
    response = client.get("/")
    assert response.status_code == 404

def test_hsm_keys_protected():
    """Ensure accessing keys without token throws 401."""
    response = client.get("/api/v1/hsm/keys")
    assert response.status_code == 401 
