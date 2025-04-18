from typing import List

from streamline.domain.metrics.performance import CycleTime, CycleTimeCalculator
from streamline.domain.sprint import SprintRepository


class GetAllSprintCycleTimesUseCase:
    """Compute cycle time use case class."""

    __slots__ = ('__calculator', '__repository')

    def __init__(self, calculator: CycleTimeCalculator, repository: SprintRepository):
        """Compute cycle time."""
        self.__calculator = calculator
        self.__repository = repository

    def execute(self) -> List[CycleTime]:
        """Compute a sprint cycle time."""
        cycle_times: List[CycleTime] = []
        for sprint in self.__repository.find_sprints():
            cycle_time = self.__calculator.calculate(sprint)
            cycle_times.append(cycle_time)

        return cycle_times
