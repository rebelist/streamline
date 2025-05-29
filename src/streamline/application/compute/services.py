from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint
from streamline.application.compute.use_cases import GetCycleTimesUseCase
from streamline.application.compute.use_cases.flow import GetLeadTimesUseCase


class FlowMetricsService:
    """Service that implements use cases for flow metrics."""

    __slots__ = ('__cycle_time_use_case', '__lead_time_use_case')

    def __init__(self, cycle_time_use_case: GetCycleTimesUseCase, lead_time_use_case: GetLeadTimesUseCase) -> None:
        self.__cycle_time_use_case = cycle_time_use_case
        self.__lead_time_use_case = lead_time_use_case

    def get_cycle_times(self, team: str) -> list[CycleTimeDataPoint]:
        """Returns a list of time series datapoints with the cycle time of all tickets."""
        return self.__cycle_time_use_case(team)

    def get_lead_times(self, team: str) -> list[LeadTimeDataPoint]:
        """Returns a list of time series datapoints with the lead time of all tickets."""
        return self.__lead_time_use_case(team)
