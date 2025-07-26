from datetime import datetime
from enum import Enum
from typing import Any

from dateutil import parser as date_parser
from tenacity import retry, stop_after_attempt

from jira.client import JIRA
from jira.resources import Issue
from rebelist.streamline.config.settings import JiraSettings
from rebelist.streamline.infrastructure.monitoring import Logger


class IssueNotStartedError(Exception):
    """Exception raised when an issue has never been in progress."""

    def __init__(self, issue: Issue) -> None:
        message = f"Ticket with ID '{issue.key}' has never been in progress."
        super().__init__(message)


class IssueNotFinishedError(Exception):
    """Exception raised when an issue has never been set to  done."""

    def __init__(self, issue: Issue) -> None:
        message = f"Ticket with ID '{issue.key}' has never set to done."
        super().__init__(message)


class TicketStatus(Enum):
    """Represent a Jira ticket status."""

    IN_PROGRESS = 'In Progress'
    DONE = 'Done'


class JiraGateway:
    """Jira gateway is a service that fetches raw sprints and issues."""

    def __init__(self, jira: JIRA, settings: JiraSettings, logger: Logger) -> None:
        self.__jira: JIRA = jira
        self.__settings = settings
        self.__logger = logger
        self.__issue_types = ', '.join(f'"{status}"' for status in self.__settings.issue_types)

    @retry(stop=stop_after_attempt(3))
    def find_sprints(self, start_at: int = 0) -> list[dict[str, Any]]:
        """Find all sprints."""
        sprints = self.__jira.sprints(self.__settings.board_id, startAt=start_at, maxResults=False, state='closed')
        documents: list[dict[str, Any]] = []
        self.__logger.info(f'Found {len(sprints)} sprints.')

        for sprint in sprints:
            jql_str = (
                f'Sprint = {sprint.id} '
                f'AND project = {self.__settings.project} '
                f'AND Teams = "{self.__settings.team}" '
                f'AND issuetype IN ({self.__issue_types}) '
            )

            self.__logger.info(f'Querying sprints tickets to JIRA: {jql_str}')

            issues = self.__jira.search_issues(
                jql_str=jql_str,
                fields='key',
            )

            document = sprint.raw
            document['opened_at'] = datetime.fromisoformat(sprint.startDate)
            document['closed_at'] = datetime.fromisoformat(sprint.completeDate)
            document['team'] = self.__settings.team
            document['tickets'] = [issue.key for issue in issues]

            del document['endDate']
            del document['activatedDate']
            del document['startDate']
            del document['completeDate']

            documents.append(document)

        return documents

    @retry(stop=stop_after_attempt(3))
    def find_tickets(self, done_at: datetime | None = None) -> list[dict[str, Any]]:
        """Find all done tickets after specific date."""
        documents: list[dict[str, Any]] = []
        sprints = self.__jira.sprints(
            self.__settings.board_id, startAt=self.__settings.sprint_offset, maxResults=False, state='closed'
        )
        filter_sprints = ','.join(str(sprint.id) for sprint in sprints)
        filter_done_at = f'AND status changed to Done AFTER "{done_at:%Y-%m-%d}"' if done_at else ''

        jql_str = (
            f'project = {self.__settings.project} '
            f'AND Sprint IN ({filter_sprints}) '
            f'AND Teams = "{self.__settings.team}" '
            f'AND issuetype IN ({self.__issue_types}) '
            f'{filter_done_at} '
            'ORDER BY created ASC'
        )

        self.__logger.info(f'Querying tickets to JIRA: {jql_str}')

        issues = self.__jira.search_issues(
            jql_str=jql_str,
            fields='key, status, summary, changelog, created, customfield_10002',
            expand='changelog',
            maxResults=False,
        )

        for issue in issues:
            try:
                started_at, resolved_at = self.__get_started_and_resolved(issue)
            except (IssueNotStartedError, IssueNotFinishedError):
                continue

            try:
                story_points = issue.fields.customfield_10002
                story_points = int(story_points) if isinstance(story_points, float) else None
            except (AttributeError, ValueError):
                story_points = None

            document = issue.raw
            document['team'] = self.__settings.team
            document['created_at'] = date_parser.parse(issue.fields.created)
            document['started_at'] = started_at
            document['resolved_at'] = resolved_at
            document['story_points'] = story_points or 0
            document['status'] = document['fields']['status']['name']

            documents.append(document)

        self.__logger.info(f'Found {len(documents)} tickets.')

        return documents

    @staticmethod
    def __get_started_and_resolved(issue: Issue) -> tuple[datetime, datetime]:
        """Determines the start and resolution timestamps of a Jira issue based on its status changes."""
        changelog = sorted(issue.changelog.histories, key=lambda h: h.created)
        in_progress_times: list[tuple[str, int]] = []
        done_times: list[tuple[str, int]] = []

        for i, history in enumerate(changelog):
            for item in history.items:
                if item.field != 'status':
                    continue
                if item.toString == TicketStatus.IN_PROGRESS.value:
                    in_progress_times.append((history.created, i))
                elif item.toString == TicketStatus.DONE.value:
                    done_times.append((history.created, i))

        if not in_progress_times:
            raise IssueNotStartedError(issue)
        if not done_times:
            raise IssueNotFinishedError(issue)

        last_in_progress_created, last_in_progress_index = in_progress_times[-1]

        for done_created, done_index in done_times:
            if done_index > last_in_progress_index:
                return (
                    date_parser.parse(last_in_progress_created),
                    date_parser.parse(done_created),
                )

        raise IssueNotFinishedError(issue)
