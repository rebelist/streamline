from datetime import datetime, timezone
from typing import Final

from rebelist.streamline.application.ingestion.jobs.models import Executable
from rebelist.streamline.config.settings import JiraSettings
from rebelist.streamline.infrastructure.jira.gateway import JiraGateway
from rebelist.streamline.infrastructure.mongo.job.repositories import Job, JobRepository
from rebelist.streamline.infrastructure.mongo.sprint import MongoSprintDocumentRepository
from rebelist.streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


class SprintJob(Executable):
    """Sprint Job: synchronizes Jira's sprint data."""

    JOB_NAME: Final[str] = 'jira_sprints'

    def __init__(
        self,
        jira_gateway: JiraGateway,
        sprint_document_repository: MongoSprintDocumentRepository,
        job_repository: JobRepository,
        settings: JiraSettings,
    ) -> None:
        self.__jira_gateway = jira_gateway
        self.__sprint_document_repository = sprint_document_repository
        self.__job_repository = job_repository
        self.__settings = settings

    def execute(self) -> None:
        """Execute sprint data synchronization."""
        team = self.__settings.team
        job = self.__job_repository.find(SprintJob.JOB_NAME, team)

        if not job:
            job = Job(name=SprintJob.JOB_NAME, team=team)

        sprint_offset = job.metadata.get('sprint_offset', self.__settings.sprint_offset)
        sprints = self.__jira_gateway.find_sprints(sprint_offset)

        next_start_at = sprint_offset
        for sprint in sprints:
            self.__sprint_document_repository.save(sprint)
            next_start_at += 1

        job.metadata = {'sprint_offset': next_start_at}
        job.executed_at = datetime.now(timezone.utc)
        self.__job_repository.save(job)


class TicketJob(Executable):
    """Ticket Job: synchronizes Jira's ticket data."""

    JOB_NAME: Final[str] = 'jira_tickets'

    def __init__(
        self,
        jira_gateway: JiraGateway,
        ticket_document_repository: MongoTicketDocumentRepository,
        job_repository: JobRepository,
        settings: JiraSettings,
    ) -> None:
        self.__jira_gateway = jira_gateway
        self.__sprint_document_repository = ticket_document_repository
        self.__job_repository = job_repository
        self.__settings = settings

    def execute(self) -> None:
        """Execute sprint data synchronization."""
        team = self.__settings.team
        job = self.__job_repository.find(TicketJob.JOB_NAME, team)

        if not job:
            job = Job(name=TicketJob.JOB_NAME, team=team)

        tickets_done_at: datetime | None = job.metadata.get('tickets_done_at')
        tickets = self.__jira_gateway.find_tickets(tickets_done_at)
        now = datetime.now(timezone.utc)

        for ticket in tickets:
            self.__sprint_document_repository.save(ticket)

        job.metadata = {'tickets_done_at': now}
        job.executed_at = now
        self.__job_repository.save(job)
