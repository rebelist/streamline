from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import MagicMock

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

    def test_sprint_creation_with_mocker(self) -> None:
        """Tests the successful creation of a Sprint instance using pytest-mock."""
        created_at = datetime(2025, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        opened_at = datetime(2025, 5, 1, 0, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2025, 5, 15, 0, 0, 0, tzinfo=timezone.utc)
        ticket_1 = Ticket('T-1', created_at, opened_at, resolved_at, 1)
        ticket_2 = Ticket('T-2', created_at, opened_at, resolved_at, 1)
        tickets: List[Ticket] = [ticket_1, ticket_2]
        sprint = Sprint(name='Sprint with Concrete', opened_at=opened_at, closed_at=resolved_at, tickets=tickets)
        assert sprint.name == 'Sprint with Concrete'
        assert sprint.opened_at == opened_at
        assert sprint.closed_at == resolved_at
        assert sprint.tickets == tickets
        assert all(isinstance(t, Ticket) for t in sprint.tickets)

    def test_all_tickets_started_within_sprint(self) -> None:
        """Tests that all tickets starting after the 6-hour offset are included."""
        opened_at = datetime(2025, 6, 10, 9, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 6, 24, 17, 0, 0, tzinfo=timezone.utc)
        offset = timedelta(hours=6)
        started_at_1 = opened_at - offset + timedelta(minutes=1)
        started_at_2 = opened_at + timedelta(days=1)

        ticket_1 = Ticket('T-101', started_at_1, started_at_1, closed_at, 3)
        ticket_2 = Ticket('T-102', started_at_2, started_at_2, closed_at, 5)
        sprint = Sprint(name='Sprint A', opened_at=opened_at, closed_at=closed_at, tickets=[ticket_1, ticket_2])

        result = sprint.started_within_sprint

        assert len(result) == 2
        assert ticket_1 in result
        assert ticket_2 in result

    def test_some_tickets_excluded_due_to_spillover(self) -> None:
        """Tests that tickets started before the 6-hour offset are excluded."""
        opened_at = datetime(2025, 6, 10, 9, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 6, 24, 17, 0, 0, tzinfo=timezone.utc)
        offset = timedelta(hours=6)
        before_offset = opened_at - offset - timedelta(minutes=1)
        after_offset = opened_at - offset + timedelta(minutes=1)

        ticket_early = Ticket('T-201', before_offset, before_offset, closed_at, 3)
        ticket_late = Ticket('T-202', after_offset, after_offset, closed_at, 5)
        sprint = Sprint(name='Sprint B', opened_at=opened_at, closed_at=closed_at, tickets=[ticket_early, ticket_late])

        result = sprint.started_within_sprint

        assert len(result) == 1
        assert ticket_late in result
        assert ticket_early not in result

    def test_no_tickets_started_within_sprint(self) -> None:
        """Tests when no tickets started within the sprint (all are spillovers)."""
        opened_at = datetime(2025, 6, 10, 9, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 6, 24, 17, 0, 0, tzinfo=timezone.utc)
        offset = timedelta(hours=6)
        before_offset = opened_at - offset - timedelta(days=1)

        ticket_1 = Ticket('T-301', before_offset, before_offset, closed_at, 2)
        ticket_2 = Ticket('T-302', before_offset, before_offset, closed_at, 1)
        sprint = Sprint(name='Sprint C', opened_at=opened_at, closed_at=closed_at, tickets=[ticket_1, ticket_2])

        result = sprint.started_within_sprint

        assert result == []

    def test_empty_ticket_list_returns_empty(self) -> None:
        """Tests that an empty ticket list results in an empty result."""
        opened_at = datetime(2025, 6, 10, 9, 0, 0, tzinfo=timezone.utc)
        closed_at = datetime(2025, 6, 24, 17, 0, 0, tzinfo=timezone.utc)
        sprint = Sprint(name='Sprint D', opened_at=opened_at, closed_at=closed_at, tickets=[])

        result = sprint.started_within_sprint

        assert result == []
