from fastapi.testclient import TestClient

from streamline.handlers.api import app


def test_cycle_time_route_exists():
    """Ensure the /performance/cycle-time endpoint is registered and returns a successful response."""
    client = TestClient(app)
    response = client.get('/v1/metrics/performance/cycle-time')
    assert response.status_code == 200
