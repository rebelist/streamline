from datetime import datetime
from unittest.mock import MagicMock, create_autospec

import pytest

from streamline.application.compute import (
    CycleTimeDataPoint,
    LeadTimeDataPoint,
    SprintCycleTimeDataPoint,
    ThroughputDataPoint,
    VelocityDataPoint,
)
from streamline.application.compute.use_cases import (
    GetCycleTimesUseCase,
    GetLeadTimesUseCase,
    GetSprintCycleTimesUseCase,
    GetThroughputUseCase,
    GetVelocityUseCase,
)
from streamline.domain.metrics.workflow import (
    CycleTimeCalculator,
    LeadTimeCalculator,
    ThroughputCalculator,
    VelocityCalculator,
)
from streamline.domain.sprint import Sprint, SprintRepository
from streamline.domain.ticket import Ticket, TicketRepository


@pytest.fixture
def velocity_calculator_mock() -> MagicMock:
    """Fixture to mock the VelocityCalculator."""
    return create_autospec(VelocityCalculator, instance=True)


@pytest.fixture
def throughput_calculator_mock() -> MagicMock:
    """Fixture to mock the ThroughputCalculator."""
    return create_autospec(ThroughputCalculator, instance=True)


@pytest.fixture
def cycle_time_calculator_mock() -> MagicMock:
    """Fixture to mock the CycleTimeCalculator."""
    return create_autospec(CycleTimeCalculator, instance=True)


@pytest.fixture
def lead_time_calculator_mock() -> MagicMock:
    """Fixture to mock the CycleTimeCalculator."""
    return create_autospec(LeadTimeCalculator, instance=True)


@pytest.fixture
def sprint_repository_mock() -> MagicMock:
    """Fixture to mock the SprintRepository."""
    return create_autospec(SprintRepository, instance=True)


@pytest.fixture
def ticket_repository_mock() -> MagicMock:
    """Fixture to mock the SprintRepository."""
    return create_autospec(TicketRepository, instance=True)


@pytest.fixture
def sprint_cycle_time_use_case(
    cycle_time_calculator_mock: MagicMock, sprint_repository_mock: MagicMock
) -> GetSprintCycleTimesUseCase:
    """Fixture to create the GetSprintCycleTimesUseCase with mocked dependencies."""
    return GetSprintCycleTimesUseCase(calculator=cycle_time_calculator_mock, sprint_repository=sprint_repository_mock)


@pytest.fixture
def cycle_time_use_case(
    cycle_time_calculator_mock: MagicMock, ticket_repository_mock: MagicMock
) -> GetCycleTimesUseCase:
    """Fixture to create the GetSprintCycleTimesUseCase with mocked dependencies."""
    return GetCycleTimesUseCase(calculator=cycle_time_calculator_mock, ticket_repository=ticket_repository_mock)


@pytest.fixture
def lead_time_use_case(lead_time_calculator_mock: MagicMock, ticket_repository_mock: MagicMock) -> GetLeadTimesUseCase:
    """Fixture to create the GetSprintCycleTimesUseCase with mocked dependencies."""
    return GetLeadTimesUseCase(calculator=lead_time_calculator_mock, ticket_repository=ticket_repository_mock)


@pytest.fixture
def throughput_use_case(
    throughput_calculator_mock: MagicMock, sprint_repository_mock: MagicMock
) -> GetThroughputUseCase:
    """Fixture to create the GetThroughputUseCase with mocked dependencies."""
    return GetThroughputUseCase(calculator=throughput_calculator_mock, sprint_repository=sprint_repository_mock)


@pytest.fixture
def velocity_use_case(velocity_calculator_mock: MagicMock, sprint_repository_mock: MagicMock) -> GetVelocityUseCase:
    """Fixture to create the GetVelocityUseCase with mocked dependencies."""
    return GetVelocityUseCase(calculator=velocity_calculator_mock, sprint_repository=sprint_repository_mock)


class TestGetSprintCycleTimesUseCase:
    """Test suite for the GetSprintCycleTimesUseCase."""

    def test_get_sprint_cycle_times_returns_correct_data(
        self,
        sprint_cycle_time_use_case: GetSprintCycleTimesUseCase,
        cycle_time_calculator_mock: MagicMock,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that GetSprintCycleTimesUseCase returns correct CycleTimeDataPoints."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)
        sprint = Sprint('Sprint 1', created_at, resolved_at, [ticket])

        sprint_repository_mock.find_by_team_name.return_value = [sprint]
        cycle_time_calculator_mock.calculate.return_value = 5.5

        result: list[SprintCycleTimeDataPoint] = sprint_cycle_time_use_case(team=team_name)

        assert len(result) == 1
        datapoint: SprintCycleTimeDataPoint = result[0]

        assert datapoint.duration == 5.5
        assert datapoint.key == 'ABC-123'
        assert datapoint.sprint == 'Sprint 1'
        assert datapoint.story_points == 1
        assert datapoint.resolved_at == int(resolved_at.timestamp() * 1000)

        cycle_time_calculator_mock.calculate.assert_called_once_with(ticket)
        sprint_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_cycle_times_with_no_sprints_returns_empty_list(
        self,
        sprint_cycle_time_use_case: GetSprintCycleTimesUseCase,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that GetSprintCycleTimesUseCase returns an empty list when no sprints are found."""
        sprint_repository_mock.find_by_team_name.return_value = []

        result: list[SprintCycleTimeDataPoint] = sprint_cycle_time_use_case('team-x')

        assert result == []
        sprint_repository_mock.find_by_team_name.assert_called_once_with('team-x')


class TestGetCycleTimesUseCase:
    """Test suite for the GetCycleTimesUseCase."""

    def test_get_cycle_times_returns_correct_data(
        self,
        cycle_time_use_case: GetCycleTimesUseCase,
        cycle_time_calculator_mock: MagicMock,
        ticket_repository_mock: MagicMock,
    ) -> None:
        """Test that GetCycleTimesUseCase returns correct CycleTimeDataPoints."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)

        ticket_repository_mock.find_by_team_name.return_value = [ticket]
        cycle_time_calculator_mock.calculate.return_value = 5.5

        result: list[CycleTimeDataPoint] = cycle_time_use_case(team=team_name)

        assert len(result) == 1
        datapoint: CycleTimeDataPoint = result[0]

        assert datapoint.duration == 5.5
        assert datapoint.key == 'ABC-123'
        assert datapoint.story_points == 1
        assert datapoint.resolved_at == int(resolved_at.timestamp() * 1000)

        cycle_time_calculator_mock.calculate.assert_called_once_with(ticket)
        ticket_repository_mock.find_by_team_name.assert_called_once_with(team_name)


class TestGetLeadTimesUseCase:
    """Test suite for the TestGetLeadTimesUseCase."""

    def test_get_lead_times_returns_correct_data(
        self,
        lead_time_use_case: GetLeadTimesUseCase,
        lead_time_calculator_mock: MagicMock,
        ticket_repository_mock: MagicMock,
    ) -> None:
        """Test that GetLeadTimesUseCase returns correct LeadTimeDataPoints."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)

        ticket_repository_mock.find_by_team_name.return_value = [ticket]
        lead_time_calculator_mock.calculate.return_value = 5.5

        result: list[LeadTimeDataPoint] = lead_time_use_case(team=team_name)

        assert len(result) == 1
        datapoint: LeadTimeDataPoint = result[0]

        assert datapoint.duration == 5.5
        assert datapoint.key == 'ABC-123'
        assert datapoint.story_points == 1
        assert datapoint.resolved_at == int(resolved_at.timestamp() * 1000)

        lead_time_calculator_mock.calculate.assert_called_once_with(ticket)
        ticket_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_lead_times_returns_empty_list(
        self,
        lead_time_use_case: GetLeadTimesUseCase,
        ticket_repository_mock: MagicMock,
    ) -> None:
        """Test that TestGetLeadTimesUseCase returns an empty list when no sprints are found."""
        ticket_repository_mock.find_by_team_name.return_value = []

        result: list[LeadTimeDataPoint] = lead_time_use_case('team-x')

        assert result == []
        ticket_repository_mock.find_by_team_name.assert_called_once_with('team-x')


class TestGetThroughputUseCase:
    """Test suite for the GetThroughputUseCase."""

    def test_get_throughput_returns_correct_data(
        self,
        throughput_use_case: GetThroughputUseCase,
        throughput_calculator_mock: MagicMock,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that GetThroughputUseCase returns correct ThroughputDataPoint."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)

        sprint = Sprint('Sprint 1', created_at, resolved_at, [ticket])
        sprint_repository_mock.find_by_team_name.return_value = [sprint]
        throughput_calculator_mock.calculate.return_value = 1

        result: list[ThroughputDataPoint] = throughput_use_case(team=team_name)

        assert len(result) == 1
        datapoint: ThroughputDataPoint = result[0]

        assert datapoint.sprint == 'Sprint 1'
        assert datapoint.residuals == 0
        assert datapoint.completed == 1
        assert datapoint.closed_at == int(resolved_at.timestamp() * 1000)

        throughput_calculator_mock.calculate.assert_called_once_with(sprint)
        sprint_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_throughput_returns_empty_list(
        self,
        throughput_use_case: GetThroughputUseCase,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that TestGetLeadTimesUseCase returns an empty list when no sprints are found."""
        sprint_repository_mock.find_by_team_name.return_value = []

        result: list[ThroughputDataPoint] = throughput_use_case('team-x')

        assert result == []
        sprint_repository_mock.find_by_team_name.assert_called_once_with('team-x')


class TestGetVelocityUseCase:
    """Test suite for the GetVelocityUseCase."""

    def test_get_velocity_returns_correct_data(
        self,
        velocity_use_case: GetVelocityUseCase,
        velocity_calculator_mock: MagicMock,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that GetVelocityUseCase returns correct VelocityDataPoint."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 10)

        sprint = Sprint('Sprint 1', created_at, resolved_at, [ticket])
        sprint_repository_mock.find_by_team_name.return_value = [sprint]
        velocity_calculator_mock.calculate.return_value = 10

        result: list[VelocityDataPoint] = velocity_use_case(team=team_name)

        assert len(result) == 1
        datapoint: VelocityDataPoint = result[0]

        assert datapoint.sprint == 'Sprint 1'
        assert datapoint.story_points_residual == 0
        assert datapoint.story_points_completed == 10

        velocity_calculator_mock.calculate.assert_called_once_with(sprint)
        sprint_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_velocity_returns_empty_list(
        self,
        velocity_use_case: GetVelocityUseCase,
        sprint_repository_mock: MagicMock,
    ) -> None:
        """Test that GetVelocityUseCase returns an empty list when no sprints are found."""
        sprint_repository_mock.find_by_team_name.return_value = []

        result: list[VelocityDataPoint] = velocity_use_case('team-x')

        assert result == []
        sprint_repository_mock.find_by_team_name.assert_called_once_with('team-x')
