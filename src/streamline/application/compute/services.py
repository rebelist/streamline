from typing import List

from streamline.application.compute.models import TimeDataPoint
from streamline.application.compute.use_cases import GetAllSprintCycleTimesUseCase


class PerformanceService:
    """Service that implements use cases for performance metrics."""

    __slots__ = '__cycle_time_use_case'

    def __init__(self, cycle_time_use_case: GetAllSprintCycleTimesUseCase):
        """Performance service initialization."""
        self.__cycle_time_use_case = cycle_time_use_case

    def get_all_sprint_cycle_times(self) -> List[TimeDataPoint]:
        """Returns a list of time series datapoints representing the cycle time of all sprints."""
        cycle_time_dataset = self.__cycle_time_use_case.execute()
        series: List[TimeDataPoint] = []
        for cycle_time in cycle_time_dataset:
            datapoint = TimeDataPoint(
                value=cycle_time.duration.total_seconds() / (60 * 60 * 8),
                timestamp=int(cycle_time.sprint.closed_at.timestamp()),
                label=cycle_time.sprint.name,
            )

            series.append(datapoint)

        return series
