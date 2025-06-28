from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from streamline.domain.metrics.flow import (
    CycleTimeCalculator,
    LeadTimeCalculator,
    ThroughputCalculator,
    VelocityCalculator,
)
from streamline.domain.sprint import Sprint
from streamline.domain.ticket import Ticket
from streamline.domain.time import WorkTimeCalculator


class TestCycleTimeCalculator:
    """Tests for the CycleTimeCalculator class."""

    def test_calculate_cycletime(self) -> None:
        """Tests the calculation of cycle time using the calendar service."""
        mock_calendar_service = MagicMock(spec=WorkTimeCalculator)
        started_at = datetime(2025, 5, 5, 10, 0, 0, tzinfo=timezone.utc)  # Monday
        resolved_at = datetime(2025, 5, 7, 12, 0, 0, tzinfo=timezone.utc)  # Wednesday
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.started_at = started_at
        mock_ticket.resolved_at = resolved_at
        expected_cycle_time = 1.75  # Example: calculated by the mock calendar

        mock_calendar_service.get_working_days_delta.return_value = expected_cycle_time

        calculator = CycleTimeCalculator(mock_calendar_service)
        cycle_time = calculator.calculate(mock_ticket)

        assert cycle_time == expected_cycle_time
        mock_calendar_service.get_working_days_delta.assert_called_once_with(started_at, resolved_at)

    def test_calculate_cycletime_different_timestamps(self) -> None:
        """Tests cycle time calculation with different start and resolve timestamps."""
        mock_calendar_service = MagicMock(spec=WorkTimeCalculator)
        started_at = datetime(2025, 5, 8, 9, 0, 0, tzinfo=timezone.utc)  # Thursday
        resolved_at = datetime(2025, 5, 9, 17, 0, 0, tzinfo=timezone.utc)  # Friday
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.started_at = started_at
        mock_ticket.resolved_at = resolved_at
        expected_cycle_time = 2.0  # Another example

        mock_calendar_service.get_working_days_delta.return_value = expected_cycle_time

        calculator = CycleTimeCalculator(mock_calendar_service)
        cycle_time = calculator.calculate(mock_ticket)

        assert cycle_time == expected_cycle_time
        mock_calendar_service.get_working_days_delta.assert_called_once_with(started_at, resolved_at)

    def test_calculate_cycletime_same_timestamp(self) -> None:
        """Tests cycle time calculation when start and resolve timestamps are the same."""
        mock_calendar_service = MagicMock(spec=WorkTimeCalculator)
        same_time = datetime(2025, 5, 12, 14, 30, 0, tzinfo=timezone.utc)  # Monday
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.started_at = same_time
        mock_ticket.resolved_at = same_time
        expected_cycle_time = 0.0

        mock_calendar_service.get_working_days_delta.return_value = expected_cycle_time

        calculator = CycleTimeCalculator(mock_calendar_service)
        cycle_time = calculator.calculate(mock_ticket)

        assert cycle_time == expected_cycle_time
        mock_calendar_service.get_working_days_delta.assert_called_once_with(same_time, same_time)

    def test_calculate_cycletime_with_timezone_info(self) -> None:
        """Tests cycle time calculation ensuring timezone information is passed to the calendar service."""
        mock_calendar_service = MagicMock(spec=WorkTimeCalculator)
        timezone_ny = timezone(timedelta(hours=-4))
        timezone_london = timezone(timedelta(hours=1))
        started_at = datetime(2025, 5, 15, 9, 0, 0, tzinfo=timezone_ny)
        resolved_at = datetime(2025, 5, 16, 17, 0, 0, tzinfo=timezone_london)
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.started_at = started_at
        mock_ticket.resolved_at = resolved_at
        expected_cycle_time = 1.5

        mock_calendar_service.get_working_days_delta.return_value = expected_cycle_time

        calculator = CycleTimeCalculator(mock_calendar_service)
        cycle_time = calculator.calculate(mock_ticket)

        assert cycle_time == expected_cycle_time
        mock_calendar_service.get_working_days_delta.assert_called_once_with(started_at, resolved_at)


class TestLeadTimeCalculator:
    """Tests for the LeadTimeCalculator class."""

    def test_calculate_leadtime(self) -> None:
        """Tests the calculation of lead time using the calendar service."""
        mock_calendar_service = MagicMock(spec=WorkTimeCalculator)
        created_at = datetime(2025, 5, 1, 10, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2025, 5, 4, 16, 0, 0, tzinfo=timezone.utc)
        mock_ticket = MagicMock(spec=Ticket)
        mock_ticket.created_at = created_at
        mock_ticket.resolved_at = resolved_at
        expected_lead_time = 2.5

        mock_calendar_service.get_working_days_delta.return_value = expected_lead_time

        calculator = LeadTimeCalculator(mock_calendar_service)
        lead_time = calculator.calculate(mock_ticket)

        assert lead_time == expected_lead_time
        mock_calendar_service.get_working_days_delta.assert_called_once_with(created_at, resolved_at)


class TestThroughputCalculator:
    """Tests for the ThroughputCalculator class."""

    def test_calculate_throughput(self) -> None:
        """Tests throughput calculation with resolved tickets within sprint."""
        closed_at = datetime(2025, 6, 1, 18, 0, 0, tzinfo=timezone.utc)

        ticket_1 = MagicMock(spec=Ticket)
        ticket_1.resolved_at = datetime(2025, 5, 30, tzinfo=timezone.utc)

        ticket_2 = MagicMock(spec=Ticket)
        ticket_2.resolved_at = datetime(2025, 6, 1, tzinfo=timezone.utc)

        ticket_3 = MagicMock(spec=Ticket)
        ticket_3.resolved_at = datetime(2025, 6, 2, tzinfo=timezone.utc)  # after sprint end

        sprint = MagicMock(spec=Sprint)
        sprint.closed_at = closed_at
        sprint.tickets = [ticket_1, ticket_2, ticket_3]

        calculator = ThroughputCalculator()
        throughput = calculator.calculate(sprint)

        assert throughput == 2

    def test_calculate_throughput_empty(self) -> None:
        """Tests throughput calculation with no tickets in sprint."""
        sprint = MagicMock(spec=Sprint)
        sprint.closed_at = datetime(2025, 6, 1, tzinfo=timezone.utc)
        sprint.tickets = []

        calculator = ThroughputCalculator()
        throughput = calculator.calculate(sprint)

        assert throughput == 0


class TestVelocityCalculator:
    """Tests for the VelocityCalculator class."""

    def test_calculate_velocity(self) -> None:
        """Tests velocity calculation summing up story points of resolved tickets."""
        closed_at = datetime(2025, 6, 1, tzinfo=timezone.utc)

        ticket_1 = MagicMock(spec=Ticket)
        ticket_1.resolved_at = datetime(2025, 5, 29, tzinfo=timezone.utc)
        ticket_1.story_points = 3

        ticket_2 = MagicMock(spec=Ticket)
        ticket_2.resolved_at = datetime(2025, 6, 1, tzinfo=timezone.utc)
        ticket_2.story_points = 5

        ticket_3 = MagicMock(spec=Ticket)
        ticket_3.resolved_at = datetime(2025, 6, 2, tzinfo=timezone.utc)  # after sprint
        ticket_3.story_points = 8

        sprint = MagicMock(spec=Sprint)
        sprint.closed_at = closed_at
        sprint.tickets = [ticket_1, ticket_2, ticket_3]

        calculator = VelocityCalculator()
        velocity = calculator.calculate(sprint)

        assert velocity == 8

    def test_calculate_velocity_empty(self) -> None:
        """Tests velocity calculation when sprint has no tickets."""
        sprint = MagicMock(spec=Sprint)
        sprint.closed_at = datetime(2025, 6, 1, tzinfo=timezone.utc)
        sprint.tickets = []

        calculator = VelocityCalculator()
        velocity = calculator.calculate(sprint)

        assert velocity == 0
