from typing import Any, List
from unittest.mock import MagicMock, Mock, create_autospec

import pytest

from rebelist.streamline.application.compute import (
    CycleTimeDataPoint,
    LeadTimeDataPoint,
    SprintCycleTimeDataPoint,
    ThroughputDataPoint,
    VelocityDataPoint,
)
from rebelist.streamline.application.compute.services import FlowMetricsService
from rebelist.streamline.application.compute.use_cases import (
    GetCycleTimesUseCase,
    GetLeadTimesUseCase,
    GetSprintCycleTimesUseCase,
    GetThroughputUseCase,
    GetVelocityUseCase,
)


@pytest.fixture
def cycle_time_sprints_use_case() -> MagicMock:
    """Fixture for mocking GetSprintCycleTimesUseCase."""
    return create_autospec(GetSprintCycleTimesUseCase, instance=True)


@pytest.fixture
def cycle_time_use_case() -> MagicMock:
    """Fixture for mocking GetCycleTimesUseCase."""
    return create_autospec(GetCycleTimesUseCase, instance=True)


@pytest.fixture
def lead_time_use_case() -> MagicMock:
    """Fixture for mocking GetLeadTimesUseCase."""
    return create_autospec(GetLeadTimesUseCase, instance=True)


@pytest.fixture
def throughput_use_case() -> MagicMock:
    """Fixture for mocking GetThroughputUseCase."""
    return create_autospec(GetThroughputUseCase, instance=True)


@pytest.fixture
def velocity_use_case() -> MagicMock:
    """Fixture for mocking GetVelocityUseCase."""
    return create_autospec(GetVelocityUseCase, instance=True)


@pytest.fixture
def flow_metrics_service(
    cycle_time_sprints_use_case: MagicMock,
    cycle_time_use_case: Mock,
    lead_time_use_case: Mock,
    throughput_use_case: Mock,
    velocity_use_case: Mock,
) -> FlowMetricsService:
    """Fixture to create FlowMetricsService with all mocked dependencies."""
    return FlowMetricsService(
        cycle_time_sprints_use_case,
        cycle_time_use_case,
        lead_time_use_case,
        throughput_use_case,
        velocity_use_case,
    )


class TestFlowMetricsService:
    """Tests for FlowMetricsService methods."""

    def test_get_cycle_times_sprints(
        self,
        flow_metrics_service: FlowMetricsService,
        cycle_time_sprints_use_case: MagicMock,
    ) -> None:
        """Tests get_cycle_times_sprints returns correct data and calls use case."""
        expected: List[SprintCycleTimeDataPoint] = [
            SprintCycleTimeDataPoint(
                duration=3.0,
                resolved_at=1234567890,
                key='ABC-1',
                sprint='Sprint 1',
            ),
        ]
        cycle_time_sprints_use_case.return_value = expected

        assert flow_metrics_service.get_sprints_cycle_times('team-x') == expected
        self.assert_call_method_called_once_with(cycle_time_sprints_use_case, 'team-x')

    def test_get_cycle_times(
        self,
        flow_metrics_service: FlowMetricsService,
        cycle_time_use_case: Mock,
    ) -> None:
        """Tests get_cycle_times returns correct data and calls use case."""
        expected: List[CycleTimeDataPoint] = [
            CycleTimeDataPoint(
                duration=4.0,
                resolved_at=1234567891,
                key='ABC-2',
                story_points=None,
            ),
        ]
        cycle_time_use_case.return_value = expected

        assert flow_metrics_service.get_cycle_times('team-x') == expected
        self.assert_call_method_called_once_with(cycle_time_use_case, 'team-x')

    def test_get_lead_times(
        self,
        flow_metrics_service: FlowMetricsService,
        lead_time_use_case: Mock,
    ) -> None:
        """Tests get_lead_times returns correct data and calls use case."""
        expected: List[LeadTimeDataPoint] = [
            LeadTimeDataPoint(
                duration=5.0,
                resolved_at=1234567892,
                key='ABC-3',
                story_points=8,
            ),
        ]
        lead_time_use_case.return_value = expected

        assert flow_metrics_service.get_lead_times('team-x') == expected
        self.assert_call_method_called_once_with(lead_time_use_case, 'team-x')

    def test_get_throughput(
        self,
        flow_metrics_service: FlowMetricsService,
        throughput_use_case: Mock,
    ) -> None:
        """Tests get_throughput returns correct data and calls use case."""
        expected: List[ThroughputDataPoint] = [
            ThroughputDataPoint(
                sprint='Sprint 1',
                completed=10,
                residuals=2,
            ),
        ]
        throughput_use_case.return_value = expected
        assert flow_metrics_service.get_throughput('team-x') == expected
        self.assert_call_method_called_once_with(throughput_use_case, 'team-x')

    def test_get_velocity(
        self,
        flow_metrics_service: FlowMetricsService,
        velocity_use_case: Mock,
    ) -> None:
        """Tests get_velocity returns correct data and calls use case."""
        expected: List[VelocityDataPoint] = [
            VelocityDataPoint(
                sprint='Sprint 1',
                story_points_residual=4,
                story_points_completed=20,
            ),
        ]
        velocity_use_case.return_value = expected

        assert flow_metrics_service.get_velocity('team-x') == expected
        self.assert_call_method_called_once_with(velocity_use_case, 'team-x')

    def assert_call_method_called_once_with(self, target: Any, team: str) -> None:
        """Assert the use case is called with the team name once."""
        target.assert_called_once()
        assert target.call_args[0][0] == team
