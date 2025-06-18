from datetime import datetime
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint
from streamline.application.compute.use_cases import GetCycleTimesUseCase
from streamline.application.compute.use_cases.flow import GetLeadTimesUseCase
from streamline.domain.metrics.workflow import CycleTimeCalculator
from streamline.domain.metrics.workflow.calculators import LeadTimeCalculator
from streamline.domain.sprint import Sprint, SprintRepository
from streamline.domain.ticket import Ticket, TicketRepository


@pytest.fixture
def cycle_time_calculator_mock(mocker: MockerFixture) -> Mock:
    """Fixture to mock the CycleTimeCalculator."""
    return mocker.Mock(spec=CycleTimeCalculator)


@pytest.fixture
def lead_time_calculator_mock(mocker: MockerFixture) -> Mock:
    """Fixture to mock the CycleTimeCalculator."""
    return mocker.Mock(spec=LeadTimeCalculator)


@pytest.fixture
def sprint_repository_mock(mocker: MockerFixture) -> Mock:
    """Fixture to mock the SprintRepository."""
    return mocker.Mock(spec=SprintRepository)


@pytest.fixture
def ticket_repository_mock(mocker: MockerFixture) -> Mock:
    """Fixture to mock the SprintRepository."""
    return mocker.Mock(spec=TicketRepository)


@pytest.fixture
def cycle_time_use_case(cycle_time_calculator_mock: Mock, sprint_repository_mock: Mock) -> GetCycleTimesUseCase:
    """Fixture to create the GetCycleTimesUseCase with mocked dependencies."""
    return GetCycleTimesUseCase(calculator=cycle_time_calculator_mock, sprint_repository=sprint_repository_mock)


@pytest.fixture
def lead_time_use_case(lead_time_calculator_mock: Mock, ticket_repository_mock: Mock) -> GetLeadTimesUseCase:
    """Fixture to create the GetCycleTimesUseCase with mocked dependencies."""
    return GetLeadTimesUseCase(calculator=lead_time_calculator_mock, repository=ticket_repository_mock)


class TestGetCycleTimesUseCase:
    """Test suite for the GetCycleTimesUseCase."""

    def test_get_cycle_times_returns_correct_data(
        self,
        cycle_time_use_case: GetCycleTimesUseCase,
        cycle_time_calculator_mock: Mock,
        sprint_repository_mock: Mock,
    ) -> None:
        """Test that GetCycleTimesUseCase returns correct CycleTimeDataPoints."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        dummy_ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)
        dummy_sprint = Sprint('Sprint 1', created_at, resolved_at, [dummy_ticket])

        sprint_repository_mock.find_by_team_name.return_value = [dummy_sprint]
        cycle_time_calculator_mock.calculate.return_value = 5.5

        result: list[CycleTimeDataPoint] = cycle_time_use_case(team=team_name)

        assert len(result) == 1
        datapoint: CycleTimeDataPoint = result[0]

        assert datapoint.duration == 5.5
        assert datapoint.key == 'ABC-123'
        assert datapoint.sprint == 'Sprint 1'
        assert datapoint.story_points == 1
        assert datapoint.resolved_at == int(resolved_at.timestamp() * 1000)

        cycle_time_calculator_mock.calculate.assert_called_once_with(dummy_ticket)
        sprint_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_cycle_times_with_no_sprints_returns_empty_list(
        self,
        cycle_time_use_case: GetCycleTimesUseCase,
        sprint_repository_mock: Mock,
    ) -> None:
        """Test that GetCycleTimesUseCase returns an empty list when no sprints are found."""
        sprint_repository_mock.find_by_team_name.return_value = []

        result: list[CycleTimeDataPoint] = cycle_time_use_case('team-x')

        assert result == []
        sprint_repository_mock.find_by_team_name.assert_called_once_with('team-x')


class TestGetLeadTimesUseCase:
    """Test suite for the TestGetLeadTimesUseCase."""

    def test_get_lead_times_returns_correct_data(
        self,
        lead_time_use_case: GetLeadTimesUseCase,
        lead_time_calculator_mock: Mock,
        ticket_repository_mock: Mock,
    ) -> None:
        """Test that GetLeadTimesUseCase returns correct LeadTimeDataPoints."""
        team_name = 'backend'
        created_at = started_at = datetime(2024, 4, 1, 12, 0)
        resolved_at = datetime(2024, 5, 1, 12, 0)
        dummy_ticket = Ticket('ABC-123', created_at, started_at, resolved_at, 1)

        ticket_repository_mock.find_by_team_name.return_value = [dummy_ticket]
        lead_time_calculator_mock.calculate.return_value = 5.5

        result: list[LeadTimeDataPoint] = lead_time_use_case(team=team_name)

        assert len(result) == 1
        datapoint: LeadTimeDataPoint = result[0]

        assert datapoint.duration == 5.5
        assert datapoint.key == 'ABC-123'
        assert datapoint.story_points == 1
        assert datapoint.resolved_at == int(resolved_at.timestamp() * 1000)

        lead_time_calculator_mock.calculate.assert_called_once_with(dummy_ticket)
        ticket_repository_mock.find_by_team_name.assert_called_once_with(team_name)

    def test_get_lead_times_returns_empty_list(
        self,
        lead_time_use_case: GetLeadTimesUseCase,
        ticket_repository_mock: Mock,
    ) -> None:
        """Test that TestGetLeadTimesUseCase returns an empty list when no sprints are found."""
        ticket_repository_mock.find_by_team_name.return_value = []

        result: list[LeadTimeDataPoint] = lead_time_use_case('team-x')

        assert result == []
        ticket_repository_mock.find_by_team_name.assert_called_once_with('team-x')
