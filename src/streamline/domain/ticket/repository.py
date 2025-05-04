from abc import ABC, abstractmethod

from streamline.domain.ticket import Ticket


class TicketRepository(ABC):
    """Ticket repository."""

    @abstractmethod
    def find(self, *keys: str) -> list[Ticket]:
        """Find tickets by it one or more keys."""
        ...
