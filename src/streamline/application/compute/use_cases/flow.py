from streamline.application.compute import (
    CycleTimeDataPoint,
    LeadTimeDataPoint,
    SprintCycleTimeDataPoint,
    ThroughputDataPoint,
    VelocityDataPoint,
)
from streamline.domain.metrics.flow import (
    CycleTimeCalculator,
    LeadTimeCalculator,
    ThroughputCalculator,
    VelocityCalculator,
)
from streamline.domain.sprint import SprintRepository
from streamline.domain.ticket import TicketRepository


class GetSprintCycleTimesUseCase:
    """Compute sprint cycle time use case."""

    def __init__(self, calculator: CycleTimeCalculator, sprint_repository: SprintRepository) -> None:
        self.__calculator = calculator
        self.__repository = sprint_repository

    def __call__(self, team: str) -> list[SprintCycleTimeDataPoint]:
        """Compute sprint cycle time for a given team."""
        datapoints: list[SprintCycleTimeDataPoint] = []
        for sprint in self.__repository.find_by_team_name(team):
            for ticket in sprint.started_within_sprint:
                duration = self.__calculator.calculate(ticket)

                datapoint = SprintCycleTimeDataPoint(
                    key=ticket.id,
                    duration=duration,
                    resolved_at=int(ticket.resolved_at.timestamp()),
                    sprint=sprint.name,
                )

                datapoints.append(datapoint)

        return datapoints


class GetCycleTimesUseCase:
    """Compute cycle time use case class."""

    def __init__(self, calculator: CycleTimeCalculator, ticket_repository: TicketRepository) -> None:
        self.__calculator = calculator
        self.__repository = ticket_repository

    def __call__(self, team: str) -> list[CycleTimeDataPoint]:
        """Compute sprint lead time for a given team."""
        datapoints: list[CycleTimeDataPoint] = []
        for ticket in self.__repository.find_by_team_name(team):
            duration = self.__calculator.calculate(ticket)

            datapoint = CycleTimeDataPoint(
                key=ticket.id,
                duration=duration,
                resolved_at=int(ticket.resolved_at.timestamp()),
                story_points=ticket.story_points,
            )

            datapoints.append(datapoint)

        return datapoints


class GetLeadTimesUseCase:
    """Compute lead time use case class."""

    def __init__(self, calculator: LeadTimeCalculator, ticket_repository: TicketRepository) -> None:
        self.__calculator = calculator
        self.__repository = ticket_repository

    def __call__(self, team: str) -> list[LeadTimeDataPoint]:
        """Compute sprint lead time for a given team."""
        datapoints: list[LeadTimeDataPoint] = []
        for ticket in self.__repository.find_by_team_name(team):
            duration = self.__calculator.calculate(ticket)

            datapoint = LeadTimeDataPoint(
                key=ticket.id,
                duration=duration,
                resolved_at=int(ticket.resolved_at.timestamp()),
                story_points=ticket.story_points,
            )

            datapoints.append(datapoint)

        return datapoints


class GetThroughputUseCase:
    """Get throughput use case class."""

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
                completed=throughput,
                residuals=len(sprint.tickets) - throughput,
            )

            datapoints.append(datapoint)

        return datapoints


class GetVelocityUseCase:
    """Get velocity use case class."""

    def __init__(self, calculator: VelocityCalculator, sprint_repository: SprintRepository) -> None:
        self.__calculator = calculator
        self.__repository = sprint_repository

    def __call__(self, team: str) -> list[VelocityDataPoint]:
        """Compute sprint velocity for a given team."""
        datapoints: list[VelocityDataPoint] = []
        for sprint in self.__repository.find_by_team_name(team):
            velocity = self.__calculator.calculate(sprint)

            datapoint = VelocityDataPoint(
                sprint=sprint.name,
                story_points_residual=sum(ticket.story_points for ticket in sprint.tickets) - velocity,
                story_points_completed=velocity,
            )

            datapoints.append(datapoint)

        return datapoints
