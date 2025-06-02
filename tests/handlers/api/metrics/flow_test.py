from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from streamline.application.compute import FlowMetricsService
from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint
from streamline.config.container import Container
from streamline.config.settings import Settings
from streamline.handlers.api.metrics import flow
from streamline.handlers.api.metrics.flow import router
from streamline.handlers.api.metrics.models import TimeUnit


class TestCycleTimeEndpoint:
    """Test suite for the /flow/cycle-time endpoint with proper mocking of dependency-injector."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Mock Settings with a fake team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Mock FlowMetricsService."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Set up FastAPI app with Container overrides and proper wiring."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container  # this is key for dependency-injector

        # Wire the container manually
        container.wire(modules=[flow])

        app.include_router(router)

        return app

    def test_cycle_time_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Test that /workflow/cycle-time returns a valid mocked response."""
        # Arrange
        mock_flow_metrics_service.get_cycle_times.return_value = [
            CycleTimeDataPoint(duration=5.5, resolved_at=1714924800, key='JIRA-123', sprint='Sprint 4', story_points=1),
            CycleTimeDataPoint(duration=3.2, resolved_at=1715011200, key='JIRA-456', sprint='Sprint 4', story_points=1),
        ]

        client = TestClient(app)

        response = client.get('/flow/cycle-time')

        assert response.status_code == 200
        data = response.json()

        assert 'datapoints' in data
        assert 'meta' in data

        assert data['meta']['metric'] == 'Cycle Time'
        assert data['meta']['unit'] == TimeUnit.DAYS.value
        assert 'description' in data['meta']

        assert len(data['datapoints']) == 2
        assert data['datapoints'][0]['key'] == 'JIRA-123'
        assert data['datapoints'][0]['story_points'] == 1


class TestLeadTimeEndpoint:
    """Test suite for the /flow/kead-time endpoint with proper mocking of dependency-injector."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Mock Settings with a fake team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Mock FlowMetricsService."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Set up FastAPI app with Container overrides and proper wiring."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container  # this is key for dependency-injector

        container.wire(modules=[flow])

        app.include_router(router)

        return app

    def test_cycle_time_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Test that /flow/cycle-time returns a valid mocked response."""
        mock_flow_metrics_service.get_lead_times.return_value = [
            LeadTimeDataPoint(duration=5.5, resolved_at=1714924800, key='JIRA-123', story_points=1),
            LeadTimeDataPoint(duration=3.2, resolved_at=1715011200, key='JIRA-456', story_points=1),
        ]

        client = TestClient(app)

        response = client.get('/flow/lead-time')

        assert response.status_code == 200
        data = response.json()

        assert 'datapoints' in data
        assert 'meta' in data

        assert data['meta']['metric'] == 'Lead Time'
        assert data['meta']['unit'] == TimeUnit.DAYS.value
        assert 'description' in data['meta']

        assert len(data['datapoints']) == 2
        assert data['datapoints'][0]['key'] == 'JIRA-123'
        assert data['datapoints'][0]['story_points'] == 1
