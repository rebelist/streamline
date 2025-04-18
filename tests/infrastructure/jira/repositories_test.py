from datetime import datetime, timezone
from typing import Union
from unittest.mock import Mock

from jira import JIRA, Issue
from pytest import fixture, raises
from pytest_mock import MockerFixture

from streamline.domain.ticket import Ticket
from streamline.infrastructure.jira import JiraSprintRepository


class TestJiraSprintRepository:
    """Tests for the JiraSprintRepository class."""

    @fixture
    def mock_jira(self, mocker: MockerFixture) -> Union[JIRA, Mock]:
        """Provides a mocked Jira client."""
        return mocker.Mock()

    @fixture
    def repository(self, mock_jira: JIRA):
        """Returns an instance of JiraSprintRepository with mock Jira."""
        return JiraSprintRepository(mock_jira, 'TeamA', 123)

    def test_initialisation(self, repository: JiraSprintRepository):
        """Test that repository is properly initialised."""
        assert isinstance(repository, JiraSprintRepository)

    def test_find_sprints_returns_sprint_with_single_ticket(
        self, repository: JiraSprintRepository, mock_jira: Mock, mocker: MockerFixture
    ):
        """Test finding a single sprint with one valid ticket."""
        sprint = mocker.Mock()
        sprint.id = 1
        sprint.name = 'Sprint X'
        sprint.startDate = '2023-09-01T00:00:00.000Z'
        sprint.completeDate = '2023-09-15T00:00:00.000Z'
        mock_jira.sprints.return_value = [sprint]

        issue = mocker.Mock()
        issue.key = 'ABC-123'
        issue.fields.resolutiondate = '2023-09-10T12:00:00.000Z'

        status_item = mocker.Mock(field='status', toString='In Progress')
        history = mocker.Mock(created='2023-09-05T10:00:00.000Z', items=[status_item])
        issue.changelog.histories = [history]

        mock_jira.search_issues.return_value = [issue]

        sprints = repository.find_sprints()

        assert len(sprints) == 1
        sprint = sprints[0]
        assert sprint.id == 1
        assert sprint.name == 'Sprint X'
        assert len(sprint.tickets) == 1

        ticket = sprint.tickets[0]
        assert isinstance(ticket, Ticket)
        assert ticket.id == 'ABC-123'
        assert ticket.started_at == datetime(2023, 9, 5, 10, 0, tzinfo=timezone.utc)
        assert ticket.resolved_at == datetime(2023, 9, 10, 12, 0, tzinfo=timezone.utc)

    def test_find_sprints_handles_multiple_sprints_and_issues(
        self, repository: JiraSprintRepository, mock_jira: Mock, mocker: MockerFixture
    ):
        """Test finding multiple sprints and multiple issues per sprint."""
        sprint1 = mocker.Mock(
            id=1, name='Sprint 1', startDate='2023-08-01T00:00:00.000Z', completeDate='2023-08-15T00:00:00.000Z'
        )
        sprint2 = mocker.Mock(
            id=2, name='Sprint 2', startDate='2023-08-16T00:00:00.000Z', completeDate='2023-08-31T00:00:00.000Z'
        )
        mock_jira.sprints.return_value = [sprint1, sprint2]

        def make_issue(key: str, created: str, resolved: str):
            issue = mocker.Mock()
            issue.key = key
            issue.fields.resolutiondate = resolved
            item = mocker.Mock(field='status', toString='In Progress')
            history = mocker.Mock(created=created, items=[item])
            issue.changelog.histories = [history]
            return issue

        issue1 = make_issue('ISSUE-1', '2023-08-05T09:00:00.000Z', '2023-08-10T18:00:00.000Z')
        issue2 = make_issue('ISSUE-2', '2023-08-20T11:30:00.000Z', '2023-08-28T17:00:00.000Z')

        mock_jira.search_issues.side_effect = [[issue1], [issue2]]

        sprints = repository.find_sprints()

        assert len(sprints) == 2
        assert sprints[0].tickets[0].id == 'ISSUE-1'
        assert sprints[1].tickets[0].id == 'ISSUE-2'

    def test_find_sprints_with_issue_missing_status_change_raises(
        self, repository: JiraSprintRepository, mock_jira: Mock, mocker: MockerFixture
    ):
        """Test that an exception is raised when an issue does not have the correct status transition."""
        sprint = mocker.Mock(
            id=100, name='Sprint Fail', startDate='2023-09-01T00:00:00.000Z', completeDate='2023-09-15T00:00:00.000Z'
        )
        mock_jira.sprints.return_value = [sprint]

        issue: Issue = mocker.Mock()
        issue.key = 'BROKEN-1'
        issue.fields.resolutiondate = '2023-09-12T10:00:00.000Z'
        issue.changelog.histories = []
        mock_jira.search_issues.return_value = [issue]

        with raises(Exception, match='Could not find started_at time for issue BROKEN-1'):
            repository.find_sprints()
