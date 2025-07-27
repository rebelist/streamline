from unittest.mock import create_autospec

import pytest
from pytest_mock import MockerFixture

from rebelist.streamline.application.compute import FlowMetricsService
from rebelist.streamline.config.settings import Settings


@pytest.fixture
def mock_settings(mocker: MockerFixture) -> Settings:
    """Create a mocked Settings instance with a fake Jira team."""
    return create_autospec(Settings, jira=mocker.MagicMock(team='FakeTeam'))


@pytest.fixture
def mock_flow_metrics_service() -> FlowMetricsService:
    """Create a mocked FlowMetricsService instance."""
    return create_autospec(FlowMetricsService, instance=True)
