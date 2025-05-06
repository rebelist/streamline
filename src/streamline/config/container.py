from __future__ import annotations

from pathlib import Path
from typing import Any, Final, Mapping, Type, cast

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Singleton, ThreadSafeSingleton
from dotenv import dotenv_values
from jira import JIRA
from pymongo import MongoClient
from pymongo.synchronous.database import Database
from workalendar.core import Calendar as WorkCalendar
from workalendar.registry import registry

from streamline.application.compute import PerformanceService
from streamline.application.compute.use_cases import GetCycleTimesUseCase
from streamline.application.ingestion.jobs import SprintJob, TicketJob
from streamline.config.settings import Settings, load_settings
from streamline.domain.metrics.workflow import CycleTimeCalculator
from streamline.domain.services import CalendarService
from streamline.infrastructure.jira import JiraGateway
from streamline.infrastructure.mongo.job import JobRepository
from streamline.infrastructure.mongo.sprint import MongoSprintDocumentRepository, MongoSprintRepository
from streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


class Container(DeclarativeContainer):
    """Dependency injection container."""

    PROJECT_ROOT: Final[str] = str(Path(__file__).resolve().parents[3])

    @staticmethod
    def create() -> Container:
        """Factory method for creating a container instance."""
        container = Container()
        container.init_resources()
        container.config.from_dict(
            {name.lower(): value for name, value in dotenv_values(f'{Container.PROJECT_ROOT}/.env').items()}
        )

        return container

    @staticmethod
    def _get_database(client: MongoClient[Any]) -> Database[Mapping[str, Any]]:
        return client.get_default_database()

    @staticmethod
    def _get_calendar(settings: Settings) -> CalendarService:
        """Provides a work_calendar instance for specific country."""
        calendar_class = cast(Type[WorkCalendar], registry.get(settings.app.region))

        if not calendar_class:
            raise ValueError(f'No WorkCalendar class found for region {settings.app.region}')

        workday_starts_at = settings.workflow.workday_starts_at
        workday_ends_at = settings.workflow.workday_ends_at
        workday_duration = settings.workflow.workday_duration

        return CalendarService(calendar_class(), workday_starts_at, workday_ends_at, workday_duration)

    ### Configuration ###
    config = Configuration(strict=True)

    settings = ThreadSafeSingleton(load_settings, f'{PROJECT_ROOT}/settings.ini')

    wiring_config = WiringConfiguration(
        auto_wire=True,
        packages=['streamline.handlers.api'],
    )

    ### Private Services ###
    __jira_client = Singleton(JIRA, server=config.jira_host, token_auth=config.jira_token)

    __mongo_client = Singleton(MongoClient, host=config.mongo_uri, tz_aware=True)

    __jira_gateway = Singleton(JiraGateway, __jira_client, settings.provided.jira)

    __calendar_service = Singleton(_get_calendar, settings.provided)

    __cycle_time_calculator = Singleton(CycleTimeCalculator, __calendar_service)

    ### Public Services ###
    database = Singleton(_get_database, __mongo_client)

    sprint_repository = Singleton(MongoSprintRepository, database)

    sprint_document_repository = Singleton(MongoSprintDocumentRepository, database)

    ticket_document_repository = Singleton(MongoTicketDocumentRepository, database)

    get_cycle_time_use_case = Singleton(GetCycleTimesUseCase, __cycle_time_calculator, sprint_repository)

    performance_service = Singleton(PerformanceService, get_cycle_time_use_case)

    job_repository = Singleton(JobRepository, database)

    sprint_job = Singleton(
        SprintJob, __jira_gateway, sprint_document_repository, job_repository, settings.provided.jira
    )

    ticket_job = Singleton(
        TicketJob, __jira_gateway, ticket_document_repository, job_repository, settings.provided.jira
    )
