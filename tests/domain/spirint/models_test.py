from datetime import datetime
from typing import List

from streamline.domain.sprint.models import Sprint
from streamline.domain.ticket import Ticket


class TestSprint:
    """Test a sprint."""

    @staticmethod
    def make_dummy_ticket(identifier: str = 'T-1') -> Ticket:
        """Helper to create a dummy Ticket instance."""
        return Ticket(identifier, datetime(2024, 1, 1, 10, 0, 0), datetime(2024, 1, 5, 15, 0, 0))

    def test_sprint_creation(self) -> None:
        """Should create a Sprint instance with correct values."""
        ticket_list: List[Ticket] = [TestSprint.make_dummy_ticket('T-1'), TestSprint.make_dummy_ticket('T-2')]
        opened_at: datetime = datetime(2024, 1, 1, 9, 0, 0)
        closed_at: datetime = datetime(2024, 1, 15, 17, 0, 0)

        sprint: Sprint = Sprint(
            id='SPR-001', name='Sprint 1', opened_at=opened_at, closed_at=closed_at, tickets=ticket_list
        )

        assert sprint.id == 'SPR-001'
        assert sprint.name == 'Sprint 1'
        assert sprint.opened_at == opened_at
        assert sprint.closed_at == closed_at
        assert sprint.tickets == ticket_list
