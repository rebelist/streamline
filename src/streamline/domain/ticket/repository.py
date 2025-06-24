from abc import ABC, abstractmethod

from streamline.domain.ticket import Ticket


class TicketRepository(ABC):
    """Ticket ticket_repository."""

    @abstractmethod
    def find_by_team_name(self, team: str) -> list[Ticket]:
        """Find a;; tickets."""
        ...
