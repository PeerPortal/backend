import pytest
from fastapi.testclient import TestClient

def test_app_import():
    """A minimal test to check if the app can be imported."""
    try:
        from app.main import app
        assert app is not None
        client = TestClient(app)
        assert client is not None
    except Exception as e:
        pytest.fail(f"Failed to import or initialize the FastAPI app: {e}")