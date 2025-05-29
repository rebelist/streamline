from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from streamline.application.compute import FlowMetricsService
from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint
from streamline.config.container import Container
from streamline.config.settings import Settings
from streamline.handlers.api.metrics.models import TimeSeriesMetadata, TimeSeriesResponse, TimeUnit

router = APIRouter()


@router.get('/flow/cycle-time')
@inject
def cycle_time(
    settings: Annotated[Settings, Depends(Provide[Container.settings])],
    flow_metrics_service: Annotated[FlowMetricsService, Depends(Provide[Container.flow_metrics_service])],
) -> TimeSeriesResponse[CycleTimeDataPoint]:
    """Get the cycle time for all tickets."""
    datapoints = flow_metrics_service.get_cycle_times(settings.jira.team)

    return TimeSeriesResponse[CycleTimeDataPoint](
        datapoints=datapoints,
        meta=TimeSeriesMetadata(
            metric='Cycle Time',
            unit=TimeUnit.DAYS,
            description='Each item represents total working time a ticket spent in progress until completion.',
        ),
    )


@router.get('/flow/lead-time')
@inject
def lead_time(
    settings: Annotated[Settings, Depends(Provide[Container.settings])],
    flow_metrics_service: Annotated[FlowMetricsService, Depends(Provide[Container.flow_metrics_service])],
) -> TimeSeriesResponse[LeadTimeDataPoint]:
    """Get the lead time for all tickets."""
    datapoints = flow_metrics_service.get_lead_times(settings.jira.team)

    return TimeSeriesResponse[LeadTimeDataPoint](
        datapoints=datapoints,
        meta=TimeSeriesMetadata(
            metric='Lead Time',
            unit=TimeUnit.DAYS,
            description='Each item represents total working time a ticket spent from creation to completion.',
        ),
    )
