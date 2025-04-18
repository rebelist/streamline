from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Ticket:
    """Represents an agile issue."""

    id: str
    started_at: datetime
    resolved_at: datetime
