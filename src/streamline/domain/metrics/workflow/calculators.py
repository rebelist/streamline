from streamline.domain.services import CalendarService
from streamline.domain.ticket import Ticket


class CycleTimeCalculator:
    """Calculate cycletime."""

    def __init__(self, calendar: CalendarService) -> None:
        self.__calendar = calendar

    def calculate(self, ticket: Ticket) -> float:
        """Calculate cycletime, returns the number of working days."""
        print(ticket)
        return self.__calendar.get_working_days_delta(ticket.started_at, ticket.resolved_at)
