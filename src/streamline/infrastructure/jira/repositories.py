from datetime import datetime
from typing import List

from dateutil import parser as date_parser
from jira.client import JIRA
from jira.resources import Issue

from streamline.domain.sprint import Sprint, SprintRepository
from streamline.domain.ticket import Ticket


class JiraSprintRepository(SprintRepository):
    """Repository that fetches sprint data from jira."""

    def __init__(self, jira: JIRA, team: str, board_id: int, start_at: int = 0) -> None:
        """Initializes the repository.

        Args:
            jira: Jira client.
            team: Team name.
            board_id: The Jira board to get sprints from.
            start_at: The index of the first sprint to return (0 based).
        """
        self.__jira: JIRA = jira
        self.__team = team
        self.__board_id: int = board_id
        self.__start_at: int = start_at

    def find_sprints(self) -> List[Sprint]:
        """Finds sprints and its tickets."""
        sprints: List[Sprint] = []
        items = self.__jira.sprints(board_id=self.__board_id, startAt=self.__start_at, state='closed')

        for item in items:
            opened_at = date_parser.parse(item.startDate)
            closed_at = date_parser.parse(item.completeDate)
            tickets: List[Ticket] = []

            issues = self.__jira.search_issues(
                jql_str=f"""
                Sprint = {item.id}
                AND status = Done
                AND Teams =  {self.__team}
                AND issuetype IN (Bug, "User Story", Spike, "Technical Story")
                AND NOT status WAS "In Progress" BEFORE {opened_at:%Y-%m-%d}
                AND status CHANGED TO "In Progress" DURING ({opened_at:%Y-%m-%d}, {closed_at:%Y-%m-%d})
                """,
                fields='key, summary, changelog, resolutiondate',
                expand='changelog',
            )

            for issue in issues:
                started_at = self.__class__.__get_started_at(issue)
                resolved_at = date_parser.parse(issue.fields.resolutiondate)
                tickets.append(Ticket(id=issue.key, started_at=started_at, resolved_at=resolved_at))

            sprints.append(Sprint(item.id, item.name, opened_at, closed_at, tickets))

        return sprints

    @staticmethod
    def __get_started_at(issue: Issue) -> datetime:
        changelog = issue.changelog

        for history in changelog.histories:
            for item in history.items:
                if item.field == 'status' and item.toString == 'In Progress':
                    if item.toString == 'In Progress':
                        return date_parser.parse(history.created)

        raise Exception(f'Could not find started_at time for issue {issue.key}')
