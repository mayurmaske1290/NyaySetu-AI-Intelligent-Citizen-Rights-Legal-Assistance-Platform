import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.incident_service import incident_store


@pytest.fixture
def client():
    incident_store._items.clear()
    return TestClient(app, raise_server_exceptions=False)
