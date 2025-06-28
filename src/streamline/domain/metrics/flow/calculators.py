from streamline.domain.sprint import Sprint
from streamline.domain.ticket import Ticket
from streamline.domain.time import WorkTimeCalculator


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
    """Calculate sprint throughput."""

    def calculate(self, sprint: Sprint) -> int:
        """Calculate the throughput of a sprint."""
        count = 0

        for ticket in sprint.tickets:
            if ticket.resolved_at <= sprint.closed_at:
                count += 1

        return count


class VelocityCalculator:
    """Calculate sprint velocity."""

    def calculate(self, sprint: Sprint) -> int:
        """Calculate the velocity of a sprint."""
        count = 0

        for ticket in sprint.tickets:
            if ticket.resolved_at <= sprint.closed_at:
                count += ticket.story_points

        return count
