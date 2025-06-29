from typing import Any, cast
from unittest.mock import MagicMock, Mock, create_autospec

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from pytest_mock import MockerFixture

from rebelist.streamline.application.compute import (
    CycleTimeDataPoint,
    FlowMetricsService,
    LeadTimeDataPoint,
    SprintCycleTimeDataPoint,
    ThroughputDataPoint,
    VelocityDataPoint,
)
from rebelist.streamline.config.container import Container
from rebelist.streamline.config.settings import Settings
from rebelist.streamline.handlers.api.metrics import flow
from rebelist.streamline.handlers.api.metrics.flow import router


class TestSprintCycleTimeEndpoint:
    """Test suite for the /flow/sprints-cycle-time endpoint with proper mocking of dependency-injector."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Create a mocked Settings instance with a fake Jira team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self) -> MagicMock:
        """Create a mocked FlowMetricsService instance."""
        return create_autospec(FlowMetricsService, instance=True)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: MagicMock) -> FastAPI:
        """Construct a FastAPI app with dependency overrides for settings and FlowMetricsService."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container
        container.wire(modules=[flow])
        app.include_router(router)

        return app

    def test_cycle_time_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: MagicMock) -> None:
        """Verify that /flow/sprints-cycle-time returns the expected mocked response."""
        # Arrange
        mock_flow_metrics_service.get_sprints_cycle_times.return_value = [
            SprintCycleTimeDataPoint(
                duration=5.5,
                resolved_at=1714924800,
                key='JIRA-123',
                sprint='Sprint 4',
            ),
            SprintCycleTimeDataPoint(
                duration=3.2,
                resolved_at=1715011200,
                key='JIRA-456',
                sprint='Sprint 4',
            ),
        ]

        client: TestClient = TestClient(app)

        # Act
        response: Response = client.get('/flow/sprints-cycle-time')
        data = cast(dict[str, Any], response.json())

        # Assert
        assert response.status_code == 200
        assert 'datapoints' in data
        assert 'meta' in data
        assert data['meta']['metric'] == 'Sprint Cycle Time'
        assert 'description' in data['meta']
        assert len(data['datapoints']) == 2
        assert data['datapoints'][0]['key'] == 'JIRA-123'


class TestLeadTimeEndpoint:
    """Test suite for the /flow/lead-time endpoint with proper mocking of dependency-injector."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Create a mocked Settings instance with a fake Jira team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Create a mocked FlowMetricsService instance."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Construct a FastAPI app with dependency overrides for settings and FlowMetricsService."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container
        container.wire(modules=[flow])
        app.include_router(router)

        return app

    def test_lead_time_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Verify that /flow/lead-time returns the expected mocked response."""
        # Arrange
        mock_flow_metrics_service.get_lead_times.return_value = [
            LeadTimeDataPoint(duration=5.5, resolved_at=1714924800, key='JIRA-123', story_points=1),
            LeadTimeDataPoint(duration=3.2, resolved_at=1715011200, key='JIRA-456', story_points=1),
        ]

        client: TestClient = TestClient(app)

        # Act
        response: Response = client.get('/flow/lead-time')
        data = cast(dict[str, Any], response.json())

        # Assert
        assert response.status_code == 200
        assert 'datapoints' in data
        assert 'meta' in data
        assert data['meta']['metric'] == 'Lead Time'
        assert 'description' in data['meta']
        assert len(data['datapoints']) == 2
        assert data['datapoints'][0]['key'] == 'JIRA-123'
        assert data['datapoints'][0]['story_points'] == 1


class TestCycleTimeEndpoint:
    """Tests for the /flow/cycle-time endpoint."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Provides a mocked Settings instance with a fake Jira team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Provides a mocked FlowMetricsService instance."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Creates a FastAPI app with the flow endpoints and overrides for testing."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container
        container.wire(modules=[flow])
        app.include_router(router)
        return app

    def test_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Checks that the /flow/cycle-time endpoint returns expected data."""
        mock_flow_metrics_service.get_cycle_times.return_value = [
            CycleTimeDataPoint(duration=2.5, resolved_at=1715000000, key='JIRA-2', story_points=5),
        ]

        client = TestClient(app)
        response = client.get('/flow/cycle-time')
        data = cast(dict[str, Any], response.json())

        assert response.status_code == 200
        assert data['meta']['metric'] == 'Cycle Time'
        assert len(data['datapoints']) == 1
        assert data['datapoints'][0]['key'] == 'JIRA-2'
        assert data['datapoints'][0]['duration'] == 2.5


class TestThroughputEndpoint:
    """Tests for the /flow/throughput endpoint."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Provides a mocked Settings instance with a fake Jira team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Provides a mocked FlowMetricsService instance."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Creates a FastAPI app with the flow endpoints and overrides for testing."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container
        container.wire(modules=[flow])
        app.include_router(router)
        return app

    def test_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Checks that the /flow/throughput endpoint returns expected data."""
        mock_flow_metrics_service.get_throughput.return_value = [
            ThroughputDataPoint(sprint='Sprint 5', completed=8, residuals=2),
        ]

        client = TestClient(app)
        response = client.get('/flow/throughput')
        data = cast(dict[str, Any], response.json())

        assert response.status_code == 200
        assert data['meta']['metric'] == 'Sprint Throughput'
        assert len(data['datapoints']) == 1
        assert data['datapoints'][0]['sprint'] == 'Sprint 5'
        assert data['datapoints'][0]['completed'] == 8


class TestVelocityEndpoint:
    """Tests for the /flow/velocity endpoint."""

    @pytest.fixture
    def mock_settings(self, mocker: MockerFixture) -> Settings:
        """Provides a mocked Settings instance with a fake Jira team."""
        return mocker.Mock(spec=Settings, jira=mocker.Mock(team='FakeTeam'))

    @pytest.fixture
    def mock_flow_metrics_service(self, mocker: MockerFixture) -> Mock:
        """Provides a mocked FlowMetricsService instance."""
        return mocker.Mock(spec=FlowMetricsService)

    @pytest.fixture
    def app(self, mock_settings: Settings, mock_flow_metrics_service: FlowMetricsService) -> FastAPI:
        """Creates a FastAPI app with the flow endpoints and overrides for testing."""
        container = Container()
        container.settings.override(mock_settings)
        container.flow_metrics_service.override(mock_flow_metrics_service)

        app = FastAPI()
        app.state.container = container
        container.wire(modules=[flow])
        app.include_router(router)
        return app

    def test_returns_valid_response(self, app: FastAPI, mock_flow_metrics_service: Mock) -> None:
        """Checks that the /flow/velocity endpoint returns expected data."""
        mock_flow_metrics_service.get_velocity.return_value = [
            VelocityDataPoint(sprint='Sprint 5', story_points_residual=3, story_points_completed=21),
        ]

        client = TestClient(app)
        response = client.get('/flow/velocity')
        data = cast(dict[str, Any], response.json())

        assert response.status_code == 200
        assert data['meta']['metric'] == 'Sprint Velocity'
        assert len(data['datapoints']) == 1
        assert data['datapoints'][0]['sprint'] == 'Sprint 5'
        assert data['datapoints'][0]['story_points_completed'] == 21
