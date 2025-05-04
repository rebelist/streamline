from datetime import datetime
from typing import Any

from dateutil import parser as date_parser
from jira.client import JIRA
from jira.resources import Issue

from streamline.config.settings import JiraSettings


class IssueNotStartedError(Exception):
    """Exception raised when an issue has never been in progress."""

    def __init__(self, issue: Issue) -> None:
        message = f"Ticket with ID '{issue.key}' has never been in progress."
        super().__init__(message)


class JiraGateway:
    """Jira gateway is a service that fetches raw sprints and issues."""

    def __init__(self, jira: JIRA, settings: JiraSettings):
        self.__jira: JIRA = jira
        self.__settings = settings

    def find_sprints(self, start_at: int = 0) -> list[dict[str, Any]]:
        """Find all sprints."""
        sprints = self.__jira.sprints(self.__settings.board_id, startAt=start_at, maxResults=False, state='closed')
        documents: list[dict[str, Any]] = []

        for sprint in sprints:
            opened_at = date_parser.parse(sprint.startDate)
            closed_at = date_parser.parse(sprint.completeDate)

            issues = self.__jira.search_issues(
                jql_str=f"""
                Sprint = {sprint.id}
                AND status = Done
                AND project = {self.__settings.project}
                AND Teams = {self.__settings.team}
                AND issuetype IN ({self.__get_statuses_as_string()})
                AND NOT status WAS "In Progress" BEFORE {opened_at:%Y-%m-%d}
                AND status CHANGED TO "In Progress" DURING ({opened_at:%Y-%m-%d}, {closed_at:%Y-%m-%d})
                """,
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

    def find_tickets(self, done_at: datetime | None = None) -> list[dict[str, Any]]:
        """Find all done tickets after specific date."""
        documents: list[dict[str, Any]] = []
        filter_done_at = f'AND status changed to Done AFTER "{done_at:%Y-%m-%d}"' if done_at else ''

        jql = f"""
        project = {self.__settings.project}
        AND status = Done
        AND Teams = {self.__settings.team}
        AND issuetype IN ({self.__get_statuses_as_string()})
        {filter_done_at}
        ORDER BY created ASC
        """

        issues = self.__jira.search_issues(
            jql_str=jql,
            fields='key, summary, changelog, resolutiondate',
            expand='changelog',
            maxResults=False,
        )

        for issue in issues:
            try:
                started_at = self.__class__.__get_started_at(issue)
            except IssueNotStartedError:
                continue

            document = issue.raw
            document['team'] = self.__settings.team
            document['started_at'] = started_at
            document['resolved_at'] = date_parser.parse(issue.fields.resolutiondate)
            documents.append(document)
        return documents

    @staticmethod
    def __get_started_at(issue: Issue) -> datetime:
        changelog = issue.changelog

        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status' and item.toString == 'In Progress':
                    return date_parser.parse(history.created)

        raise IssueNotStartedError(issue)

    def __get_statuses_as_string(self) -> str:
        return ', '.join(f'"{status}"' for status in self.__settings.issue_statuses)
