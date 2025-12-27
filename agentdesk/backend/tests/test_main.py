from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_agents():
    response = client.get("/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
