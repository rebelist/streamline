from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from streamline.application.compute import PerformanceService
from streamline.application.compute.models import CycleTimeDataPoint
from streamline.config.container import Container
from streamline.config.settings import Settings
from streamline.handlers.api.v1 import metrics
from streamline.handlers.api.v1.models import TimeUnit


class TestCycleTimeEndpoint:
    """Test suite for the /workflow/cycle-time endpoint with proper mocking of dependency-injector."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Mock Settings with a fake team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_performance_service(self, mocker: MockerFixture) -> Mock:
        """Mock PerformanceService."""
        return mocker.Mock(spec=PerformanceService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_performance_service: PerformanceService) -> FastAPI:
        """Set up FastAPI app with Container overrides and proper wiring."""
        container = Container()
        container.settings.override(mock_settings)
        container.performance_service.override(mock_performance_service)

        app = FastAPI()
        app.state.container = container  # this is key for dependency-injector

        # Wire the container manually
        container.wire(modules=[metrics])

        app.include_router(metrics.router)

        return app

    def test_cycle_time_returns_valid_response(self, app: FastAPI, mock_performance_service: Mock) -> None:
        """Test that /workflow/cycle-time returns a valid mocked response."""
        # Arrange
        mock_performance_service.get_cycle_times.return_value = [
            CycleTimeDataPoint(duration=5.5, resolved_at=1714924800, ticket='JIRA-123', sprint='Sprint 42'),
            CycleTimeDataPoint(duration=3.2, resolved_at=1715011200, ticket='JIRA-456', sprint='Sprint 42'),
        ]

        client = TestClient(app)

        # Act
        response = client.get('/workflow/cycle-time')

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert 'datapoints' in data
        assert 'meta' in data

        assert data['meta']['metric'] == 'Cycle Time'
        assert data['meta']['unit'] == TimeUnit.DAYS.value
        assert 'description' in data['meta']

        assert len(data['datapoints']) == 2
        assert data['datapoints'][0]['ticket'] == 'JIRA-123'
