from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any, Type, cast

from fastapi import Depends
from jira import JIRA
from workalendar.core import Calendar as WorkCalendar
from workalendar.registry import registry

from streamline.application.compute import PerformanceService
from streamline.application.compute.use_cases import GetAllSprintCycleTimesUseCase
from streamline.config.settings import settings as app_settings
from streamline.domain.metrics.performance import CycleTimeCalculator
from streamline.domain.services import CalendarService
from streamline.infrastructure.jira import JiraSprintRepository


@lru_cache()
def _on_settings() -> Any:
    """Provides project settings for injection."""
    return app_settings


@lru_cache()
def _on_calendar(settings: Annotated[Any, Depends(_on_settings)]) -> CalendarService:
    """Provides a work_calendar instance for specific country."""
    region = settings.app.get('region')
    calendar_class = cast(Type[WorkCalendar], registry.get(region))

    if not calendar_class:
        raise ValueError(f'No WorkCalendar class found for region {region}')

    workday_starts_at = datetime.strptime(settings.team.get('workday_starts_at'), '%H:%M').time()
    workday_ends_at = datetime.strptime(settings.team.get('workday_ends_at'), '%H:%M').time()
    workday_duration = settings.team.get('workday_duration')

    return CalendarService(calendar_class(), workday_starts_at, workday_ends_at, workday_duration)


@lru_cache()
def _on_jira_client(settings: Annotated[Any, Depends(_on_settings)]) -> JIRA:
    """Provides a jira client for injection."""
    return JIRA(server=settings.get('jira_host'), token_auth=settings.get('jira_token'))


@lru_cache()
def _on_sprint_repository(
    client: Annotated[Any, Depends(_on_jira_client)], settings: Annotated[Any, Depends(_on_settings)]
) -> JiraSprintRepository:
    """Provides a sprint repository  for injection."""
    return JiraSprintRepository(
        client, settings.team.get('name'), settings.jira.get('board_id'), settings.jira.get('sprint_start_at')
    )


@lru_cache()
def _on_cycle_time_calculator(calendar: Annotated[CalendarService, Depends(_on_calendar)]) -> CycleTimeCalculator:
    """Provides a cyle time calculator."""
    return CycleTimeCalculator(calendar)


@lru_cache()
def _on_calculate_cycle_time_use_case(
    calculator: Annotated[CycleTimeCalculator, Depends(_on_cycle_time_calculator)],
    repository: Annotated[JiraSprintRepository, Depends(_on_sprint_repository)],
) -> GetAllSprintCycleTimesUseCase:
    """Provides a calculate cycle time use case."""
    return GetAllSprintCycleTimesUseCase(calculator, repository)


@lru_cache()
def on_performance_service(
    calculate_cycle_time_use_case: Annotated[GetAllSprintCycleTimesUseCase, Depends(_on_calculate_cycle_time_use_case)],
) -> PerformanceService:
    """Provides a ticket repository for injection."""
    return PerformanceService(calculate_cycle_time_use_case)
