from dataclasses import dataclass
from datetime import datetime

from streamline.domain.ticket import Ticket


@dataclass(frozen=True)
class Sprint:
    """Represents an agile iteration."""

    name: str
    opened_at: datetime
    closed_at: datetime
    tickets: list[Ticket]
