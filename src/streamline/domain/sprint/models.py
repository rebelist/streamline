from dataclasses import dataclass
from datetime import datetime
from typing import List

from streamline.domain.ticket import Ticket


@dataclass(frozen=True)
class Sprint:
    """Represents an agile iteration."""

    id: str
    name: str
    opened_at: datetime
    closed_at: datetime
    tickets: List[Ticket]
