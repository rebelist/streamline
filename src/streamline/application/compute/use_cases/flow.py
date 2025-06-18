from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint, ThroughputDataPoint
from streamline.domain.metrics.workflow import CycleTimeCalculator
from streamline.domain.metrics.workflow.calculators import LeadTimeCalculator, ThroughputCalculator
from streamline.domain.sprint import SprintRepository
from streamline.domain.ticket import TicketRepository


class GetCycleTimesUseCase:
    """Compute cycle time use case class."""

    __slots__ = ('__calculator', '__repository')

    def __init__(self, calculator: CycleTimeCalculator, sprint_repository: SprintRepository) -> None:
        self.__calculator = calculator
        self.__repository = sprint_repository

    def __call__(self, team: str) -> list[CycleTimeDataPoint]:
        """Compute sprint cycle time for a given team."""
        datapoints: list[CycleTimeDataPoint] = []
        for sprint in self.__repository.find_by_team_name(team):
            for ticket in sprint.tickets:
                if not (sprint.opened_at <= ticket.started_at <= sprint.closed_at):
                    continue

                duration = self.__calculator.calculate(ticket)

                datapoint = CycleTimeDataPoint(
                    key=ticket.id,
                    duration=duration,
                    resolved_at=int(ticket.resolved_at.timestamp() * 1000),
                    story_points=ticket.story_points,
                    sprint=sprint.name,
                )

                datapoints.append(datapoint)

        return datapoints


class GetLeadTimesUseCase:
    """Compute lead time use case class."""

    __slots__ = ('__calculator', '__repository')

    def __init__(self, calculator: LeadTimeCalculator, repository: TicketRepository) -> None:
        self.__calculator = calculator
        self.__repository = repository

    def __call__(self, team: str) -> list[LeadTimeDataPoint]:
        """Compute sprint lead time for a given team."""
        datapoints: list[LeadTimeDataPoint] = []
        for ticket in self.__repository.find_by_team_name(team):
            duration = self.__calculator.calculate(ticket)

            datapoint = LeadTimeDataPoint(
                key=ticket.id,
                duration=duration,
                resolved_at=int(ticket.resolved_at.timestamp() * 1000),
                story_points=ticket.story_points,
            )

            datapoints.append(datapoint)

        return datapoints


class GetThroughputUseCase:
    """Get throughput use case class."""

    __slots__ = ('__calculator', '__repository')

    def __init__(self, calculator: ThroughputCalculator, sprint_repository: SprintRepository) -> None:
        self.__calculator = calculator
        self.__repository = sprint_repository

    def __call__(self, team: str) -> list[ThroughputDataPoint]:
        """Compute sprint throughtput for a given team."""
        datapoints: list[ThroughputDataPoint] = []
        for sprint in self.__repository.find_by_team_name(team):
            throughput = self.__calculator.calculate(sprint)

            datapoint = ThroughputDataPoint(
                sprint=sprint.name,
                closed_at=int(sprint.closed_at.timestamp() * 1000),
                completed=throughput,
                residuals=len(sprint.tickets) - throughput,
            )

            datapoints.append(datapoint)

        return datapoints
