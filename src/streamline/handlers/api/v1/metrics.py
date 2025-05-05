from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from streamline.application.compute import PerformanceService
from streamline.application.compute.models import CycleTimeDataPoint
from streamline.config.container import Container
from streamline.config.settings import Settings
from streamline.handlers.api.v1.models import TimeSeriesMetadata, TimeSeriesResponse, TimeUnit

router = APIRouter()


@router.get('/workflow/cycle-time')
@inject
def cycle_time(
    settings: Annotated[Settings, Depends(Provide[Container.settings])],
    performance_service: Annotated[PerformanceService, Depends(Provide[Container.performance_service])],
) -> TimeSeriesResponse[CycleTimeDataPoint]:
    """Get the cycle time for all sprints."""
    datapoints = performance_service.get_cycle_times(settings.jira.team)

    return TimeSeriesResponse[CycleTimeDataPoint](
        datapoints=datapoints,
        meta=TimeSeriesMetadata(
            metric='Cycle Time',
            unit=TimeUnit.DAYS,
            description='Represents the total time a ticket (datapoint) was in progress, counting working hours only.',
        ),
    )
