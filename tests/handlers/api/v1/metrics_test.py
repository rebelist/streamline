from typing import Union
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import fixture

from streamline.application.compute import PerformanceService
from streamline.application.compute.models import TimeDataPoint
from streamline.config.dependencies import on_performance_service
from streamline.handlers.api.v1.metrics import router


@fixture
def mock_service() -> Union[PerformanceService, Mock]:
    """PerformanceService mock."""
    mock = Mock(spec=PerformanceService)
    mock.get_all_sprint_cycle_times.return_value = [
        TimeDataPoint(value=5, timestamp=1700000000, label='Sprint 1'),
        TimeDataPoint(value=3, timestamp=1700001000, label='Sprint 2'),
    ]
    return mock


@fixture
def test_app(mock_service: Mock) -> FastAPI:
    """Create a test FastAPI app with overridden dependency."""
    app = FastAPI()
    app.include_router(router)

    app.dependency_overrides[on_performance_service] = lambda: mock_service  # type: ignore[attr-defined]
    return app


def test_cycle_time_returns_expected_data(test_app: FastAPI):
    """Test the /performance/cycle-time endpoint returns cycle time data."""
    client = TestClient(test_app)

    response = client.get('/performance/cycle-time')

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json() == {
        'target': 'cycletime',
        'datapoints': [
            {
                'value': 5.0,
                'timestamp': 1700000000,
                'label': 'Sprint 1',
            },
            {
                'value': 3.0,
                'timestamp': 1700001000,
                'label': 'Sprint 2',
            },
        ],
        'type': 'timeseries',
        'unit': 'days',
    }
