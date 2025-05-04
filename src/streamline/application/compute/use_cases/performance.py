from streamline.application.compute.models import CycleTimeDataPoint
from streamline.domain.metrics.performance import CycleTimeCalculator
from streamline.domain.sprint import SprintRepository


class GetCycleTimesUseCase:
    """Compute cycle time use case class."""

    __slots__ = ('__calculator', '__repository')

    def __init__(self, calculator: CycleTimeCalculator, sprint_repository: SprintRepository):
        self.__calculator = calculator
        self.__repository = sprint_repository

    def __call__(self, team: str) -> list[CycleTimeDataPoint]:
        """Compute a jira_sprint cycle time for a given team."""
        datapoints: list[CycleTimeDataPoint] = []
        for sprint in self.__repository.find_by_team_name(team):
            for ticket in sprint.tickets:
                duration = self.__calculator.calculate(ticket)

                datapoint = CycleTimeDataPoint(
                    duration=duration,
                    resolved_at=int(ticket.resolved_at.timestamp() * 1000),
                    ticket=ticket.id,
                    sprint=sprint.name,
                )

                datapoints.append(datapoint)

        return datapoints
