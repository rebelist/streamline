from dataclasses import dataclass
from datetime import datetime, timedelta

from streamline.domain.ticket import Ticket


@dataclass(frozen=True)
class Sprint:
    """Represents an agile iteration."""

    name: str
    opened_at: datetime
    closed_at: datetime
    tickets: list[Ticket]

    @property
    def started_within_sprint(self) -> list[Ticket]:
        """Returns tickets started during the sprint, excluding spillovers."""
        tickets: list[Ticket] = []
        # A 6-hour offset accounts for work begun just before the sprint start.
        sprint_datetime_with_offset = self.opened_at - timedelta(hours=6)
        for ticket in self.tickets:
            if ticket.started_at < sprint_datetime_with_offset:
                continue
            tickets.append(ticket)

        return tickets
