from datetime import datetime
from zoneinfo import ZoneInfo


class DateTimeNormalizer:
    """Service class responsible for normalizing datetime objects to a specific timezone."""

    def __init__(self, timezone: ZoneInfo):
        self.timezone = timezone

    def normalize(self, target: datetime) -> datetime:
        """Convert the given datetime to the target timezone."""
        if target.tzinfo is None:
            target = target.replace(tzinfo=ZoneInfo('UTC'))
        print(self.timezone)
        return target.astimezone(self.timezone)
