from datetime import datetime, timedelta, timezone

from streamline.domain.ticket import Ticket


class TestTicket:
    """Tests for the Ticket dataclass."""

    def test_ticket_creation(self: 'TestTicket') -> None:
        """Tests the successful creation of a Ticket instance."""
        started_at = datetime(2025, 5, 5, 10, 0, 0, tzinfo=timezone.utc)
        resolved_at = datetime(2025, 5, 7, 12, 0, 0, tzinfo=timezone.utc)
        ticket = Ticket(id='TASK-123', started_at=started_at, resolved_at=resolved_at)
        assert ticket.id == 'TASK-123'
        assert ticket.started_at == started_at
        assert ticket.resolved_at == resolved_at

    def test_ticket_with_different_timezones(self: 'TestTicket') -> None:
        """Tests the creation of a Ticket with started and resolved times in different timezones."""
        tz_ny = timezone(timedelta(hours=-4))
        tz_london = timezone(timedelta(hours=1))
        started_at = datetime(2025, 5, 12, 8, 0, 0, tzinfo=tz_ny)
        resolved_at = datetime(2025, 5, 14, 16, 0, 0, tzinfo=tz_london)
        ticket = Ticket(id='TICKET-789', started_at=started_at, resolved_at=resolved_at)
        assert ticket.started_at == started_at
        assert ticket.resolved_at == resolved_at

    def test_ticket_with_same_start_and_resolve_time(self: 'TestTicket') -> None:
        """Tests the creation of a Ticket where started and resolved times are the same."""
        same_time = datetime(2025, 5, 15, 12, 30, 0, tzinfo=timezone.utc)
        ticket = Ticket(id='SAME-TIME-1', started_at=same_time, resolved_at=same_time)
        assert ticket.started_at == same_time
        assert ticket.resolved_at == same_time
