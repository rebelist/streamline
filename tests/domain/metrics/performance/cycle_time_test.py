from datetime import datetime, timedelta
from typing import List

from pytest import fixture, raises
from pytest_mock import MockFixture

from streamline.domain.metrics.performance import CycleTime, CycleTimeCalculator
from streamline.domain.services import CalendarService
from streamline.domain.sprint import Sprint
from streamline.domain.ticket import Ticket


class TestCycleTimeCalculator:
    """Test cycle time calculator."""

    def make_ticket(self, identifier: str, start: datetime, end: datetime) -> Ticket:
        """Create a dummy ticket."""
        return Ticket(id=identifier, started_at=start, resolved_at=end)

    @fixture
    def tickets(self) -> List[Ticket]:
        """Create dummy tickets."""
        return [
            self.make_ticket('T-1', datetime(2024, 1, 1, 9), datetime(2024, 1, 2, 9)),  # 24h
            self.make_ticket('T-2', datetime(2024, 1, 3, 9), datetime(2024, 1, 3, 21)),  # 12h
            self.make_ticket('T-3', datetime(2024, 1, 4, 9), datetime(2024, 1, 6, 9)),  # 48h
        ]

    @fixture
    def sprint(self, tickets: List[Ticket]) -> Sprint:
        """Create a dummy sprint."""
        return Sprint(
            id='SPR-001',
            name='Sprint 1',
            opened_at=datetime(2024, 1, 1),
            closed_at=datetime(2024, 1, 10),
            tickets=tickets,
        )

    def test_calculate_cycle_time_returns_correct_median(self, mocker: MockFixture, sprint: Sprint) -> None:
        """Should calculate the correct median cycle time using the mocked calendar."""
        calendar_mock = mocker.Mock(spec=CalendarService)
        calendar_mock.get_working_hours_delta.side_effect = [24.0, 12.0, 48.0]

        calculator = CycleTimeCalculator(calendar=calendar_mock)
        result: CycleTime = calculator.calculate(sprint)

        assert result.sprint == sprint
        assert result.duration == timedelta(hours=24)
        assert calendar_mock.get_working_hours_delta.call_count == 3

    def test_calculate_with_empty_tickets_raises_error(self, mocker: MockFixture) -> None:
        """Should raise ValueError when sprint has no tickets."""
        empty_sprint = Sprint(
            id='SPR-002',
            name='Empty Sprint',
            opened_at=datetime(2024, 2, 1),
            closed_at=datetime(2024, 2, 10),
            tickets=[],
        )

        calendar_mock = mocker.Mock(spec=CalendarService)
        calculator = CycleTimeCalculator(calendar=calendar_mock)

        with raises(ValueError):
            calculator.calculate(empty_sprint)
