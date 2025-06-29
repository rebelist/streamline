from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Ticket:
    """Represents an agile issue."""

    id: str
    created_at: datetime
    started_at: datetime
    resolved_at: datetime
    story_points: int
