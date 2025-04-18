from dataclasses import dataclass
from datetime import timedelta
from statistics import median
from typing import List

from streamline.domain.services import CalendarService
from streamline.domain.sprint import Sprint


@dataclass(frozen=True)
class CycleTime:
    """Represent a cycletime."""

    sprint: Sprint
    duration: timedelta


class CycleTimeCalculator:
    """Calculate cycletime."""

    def __init__(self, calendar: CalendarService) -> None:
        """Initialize cycletime calculator."""
        self.__calendar = calendar

    def calculate(self, sprint: Sprint) -> CycleTime:
        """Calculate cycletime."""
        deltas: List[float] = []
        for ticket in sprint.tickets:
            hours = self.__calendar.get_working_hours_delta(ticket.started_at, ticket.resolved_at)
            deltas.append(hours)

        median_hours = median(deltas)

        return CycleTime(sprint, timedelta(hours=median_hours))
