from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from streamline.domain.sprint import Sprint
from streamline.domain.ticket import Ticket


class TestSprint:
    """Tests for the Sprint dataclass."""

    def test_sprint_creation(self) -> None:
        """Tests the successful creation of a Sprint instance."""
        opened_at = datetime(2025, 5, 5, 0, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 5, 19, 0, 0, 0, tzinfo=timezone.utc)
        mock_ticket_1 = MagicMock(spec=Ticket)
        mock_ticket_2 = MagicMock(spec=Ticket)
        tickets: List[Ticket] = [mock_ticket_1, mock_ticket_2]
        sprint = Sprint(name='Sprint 1', opened_at=opened_at, closed_at=closed_at, tickets=tickets)
        assert sprint.name == 'Sprint 1'
        assert sprint.opened_at == opened_at
        assert sprint.closed_at == closed_at
        assert sprint.tickets == tickets

    def test_sprint_with_empty_tickets(self) -> None:
        """Tests the creation of a Sprint with an empty list of tickets."""
        opened_at = datetime(2025, 5, 12, 0, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 5, 26, 0, 0, 0, tzinfo=timezone.utc)
        sprint = Sprint(name='Sprint 3', opened_at=opened_at, closed_at=closed_at, tickets=[])
        assert sprint.tickets == []

    def test_sprint_with_different_timezone_dates(self) -> None:
        """Tests the creation of a Sprint with opened and closed dates in different timezones."""
        tz_ny = timezone(timedelta(hours=-4))
        tz_london = timezone(timedelta(hours=1))
        opened_at = datetime(2025, 5, 15, 10, 0, 0, tzinfo=tz_ny)
        closed_at = datetime(2025, 5, 29, 18, 0, 0, tzinfo=tz_london)
        mock_ticket = MagicMock(spec=Ticket)
        sprint = Sprint(name='Sprint 4', opened_at=opened_at, closed_at=closed_at, tickets=[mock_ticket])
        assert sprint.opened_at == opened_at
        assert sprint.closed_at == closed_at
        assert isinstance(sprint.tickets[0], MagicMock)  # Verify it's still the mock

    def test_sprint_creation_with_mocker(self, mocker: MockerFixture) -> None:
        """Tests the successful creation of a Sprint instance using pytest-mock."""
        created_at = datetime(2025, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        opened_at = datetime(2025, 5, 1, 0, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2025, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
        ticket_1 = Ticket('T-1', created_at, opened_at, resolved_at)
        ticket_2 = Ticket('T-2', created_at, opened_at, resolved_at)
        tickets: List[Ticket] = [ticket_1, ticket_2]
        sprint = Sprint(name='Sprint with Concrete', opened_at=opened_at, closed_at=resolved_at, tickets=tickets)
        assert sprint.name == 'Sprint with Concrete'
        assert sprint.opened_at == opened_at
        assert sprint.closed_at == resolved_at
        assert sprint.tickets == tickets
        assert all(isinstance(t, Ticket) for t in sprint.tickets)
