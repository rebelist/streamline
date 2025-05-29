from streamline.domain.ticket import Ticket
from streamline.domain.time import WorkTimeCalculator


class CycleTimeCalculator:
    """Calculate cycletime."""

    def __init__(self, calendar: WorkTimeCalculator) -> None:
        self.__calendar = calendar

    def calculate(self, ticket: Ticket) -> float:
        """Calculate cycletime, returns the number of working days."""
        return self.__calendar.get_working_days_delta(ticket.started_at, ticket.resolved_at)


class LeadTimeCalculator:
    """Calculate lead time."""

    def __init__(self, calendar: WorkTimeCalculator) -> None:
        self.__calendar = calendar

    def calculate(self, ticket: Ticket) -> float:
        """Calculate lead time, returns the number of working days."""
        return self.__calendar.get_working_days_delta(ticket.created_at, ticket.resolved_at)
