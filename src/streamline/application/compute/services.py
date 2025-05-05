from streamline.application.compute.models import CycleTimeDataPoint
from streamline.application.compute.use_cases import GetCycleTimesUseCase


class PerformanceService:
    """Service that implements use cases for workflow metrics."""

    __slots__ = '__cycle_time_use_case'

    def __init__(self, cycle_time_use_case: GetCycleTimesUseCase) -> None:
        self.__cycle_time_use_case = cycle_time_use_case

    def get_cycle_times(self, team: str) -> list[CycleTimeDataPoint]:
        """Returns a list of time series datapoints representing the cycle time of all tickets."""
        return self.__cycle_time_use_case(team)
