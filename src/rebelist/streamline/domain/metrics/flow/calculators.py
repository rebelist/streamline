from datetime import datetime, time

from rebelist.streamline.domain.sprint import Sprint
from rebelist.streamline.domain.ticket import Ticket
from rebelist.streamline.domain.time import WorkTimeCalculator


class CycleTimeCalculator:
    """Calculate ticket cycletime."""

    def __init__(self, calendar: WorkTimeCalculator) -> None:
        self.__calendar = calendar

    def calculate(self, ticket: Ticket) -> float:
        """Calculate cycletime, returns the number of working days."""
        return self.__calendar.get_working_days_delta(ticket.started_at, ticket.resolved_at)


class LeadTimeCalculator:
    """Calculate ticket lead time."""

    def __init__(self, calendar: WorkTimeCalculator) -> None:
        self.__calendar = calendar

    def calculate(self, ticket: Ticket) -> float:
        """Calculate lead time, returns the number of working days."""
        return self.__calendar.get_working_days_delta(ticket.created_at, ticket.resolved_at)


class ThroughputCalculator:
    """Calculates the number of tickets resolved before the sprint officially ends."""

    def __init__(self, sprint_close_time: time | None = None) -> None:
        self._sprint_close_time = sprint_close_time

    def calculate(self, sprint: Sprint) -> int:
        """Calculate the throughput of a sprint: tickets resolved before sprint close time."""
        effective_close_time = self._get_effective_close_datetime(sprint.closed_at)

        return sum(1 for ticket in sprint.tickets if ticket.resolved_at and ticket.resolved_at <= effective_close_time)

    def _get_effective_close_datetime(self, closed_at: datetime) -> datetime:
        """Combine the sprint's closed date with the configured closing time, if any."""
        if not self._sprint_close_time:
            return closed_at

        return closed_at.replace(hour=self._sprint_close_time.hour, minute=self._sprint_close_time.minute)


class VelocityCalculator:
    """Calculates sprint velocity based on resolved story points before sprint closes."""

    def __init__(self, sprint_close_time: time | None = None) -> None:
        self._sprint_close_time = sprint_close_time

    def calculate(self, sprint: Sprint) -> int:
        """Calculate the total story points of tickets resolved before sprint close time."""
        effective_close_time = self._get_effective_close_datetime(sprint.closed_at)

        return sum(
            ticket.story_points
            for ticket in sprint.tickets
            if ticket.resolved_at and ticket.resolved_at <= effective_close_time
        )

    def _get_effective_close_datetime(self, closed_at: datetime) -> datetime:
        """Combine the sprint's close date with the configured closing time, if any."""
        if not self._sprint_close_time:
            return closed_at

        return closed_at.replace(
            hour=self._sprint_close_time.hour,
            minute=self._sprint_close_time.minute,
        )
