from datetime import datetime

from streamline.domain.ticket import Ticket


class TestTicket:
    """Test a ticket class."""

    def test_ticket_creation(self) -> None:
        """Should create a Ticket instance with correct values."""
        ticket_id: str = 'TICKET-123'
        start_time: datetime = datetime(2024, 1, 1, 10, 0, 0)
        resolve_time: datetime = datetime(2024, 1, 2, 12, 0, 0)

        ticket: Ticket = Ticket(id=ticket_id, started_at=start_time, resolved_at=resolve_time)

        assert ticket.id == ticket_id
        assert ticket.started_at == start_time
        assert ticket.resolved_at == resolve_time
