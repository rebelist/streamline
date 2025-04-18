from typing import Annotated

from fastapi import APIRouter, Depends

from streamline.application.compute import PerformanceService
from streamline.config.dependencies import on_performance_service
from streamline.handlers.api.v1.models import TimeSeriesResponse, TimeUnit

router = APIRouter()


@router.get('/performance/cycle-time')
async def cycle_time(
    performance_service: Annotated[PerformanceService, Depends(on_performance_service)],
) -> TimeSeriesResponse:
    """Get the cycle time for all sprints."""
    datapoints = performance_service.get_all_sprint_cycle_times()

    return TimeSeriesResponse(
        target='cycletime',
        datapoints=datapoints,
        type='timeseries',
        unit=TimeUnit.DAYS,
    )
