from datetime import datetime, timezone
from typing import Final

from streamline.application.ingestion.models import Executable
from streamline.config.settings import JiraSettings
from streamline.infrastructure.jira.gateway import JiraGateway
from streamline.infrastructure.mongo.jira_sprint import MongoSprintDocumentRepository
from streamline.infrastructure.mongo.jira_ticket import MongoTicketDocumentRepository
from streamline.infrastructure.mongo.job.repositories import Job, JobRepository


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
        """Execute jira_sprint data synchronization."""
        team = self.__settings.team
        job = self.__job_repository.find(SprintJob.JOB_NAME, team)

        if not job:
            job = Job(name=SprintJob.JOB_NAME, team=team)

        sprint_start_at = job.metadata.get('sprint_index_start_at', self.__settings.sprint_start_at)
        sprints = self.__jira_gateway.find_sprints(sprint_start_at)

        next_start_at = sprint_start_at
        for sprint in sprints:
            self.__sprint_document_repository.save(sprint)
            next_start_at += 1

        job.metadata = {'sprint_index_start_at': next_start_at}
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
        """Execute jira_sprint data synchronization."""
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
