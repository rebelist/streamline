from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from dateutil.tz import tzutc
from jira.client import JIRA
from jira.resources import Issue

from streamline.config.settings import JiraSettings
from streamline.infrastructure.jira.gateway import JiraGateway


@pytest.fixture
def mock_jira_client() -> MagicMock:
    """Mock the Jira client."""
    return MagicMock(spec=JIRA)


@pytest.fixture
def mock_jira_settings() -> MagicMock:
    """Mock the Jira settings."""
    settings = MagicMock(spec=JiraSettings)
    settings.board_id = 123
    settings.project = 'TEST'
    settings.team = 'TestTeam'
    settings.issue_statuses = ['Task', 'Bug']
    return settings


def test_jira_gateway_find_sprints_success(mock_jira_client: MagicMock, mock_jira_settings: MagicMock) -> None:
    """Test finding sprints successfully."""
    mock_sprint = MagicMock()
    mock_sprint.id = 1
    mock_sprint.startDate = '2025-05-01T00:00:00.000+0000'
    mock_sprint.completeDate = '2025-05-15T00:00:00.000+0000'
    mock_sprint.raw = {
        'id': 1,
        'name': 'Sprint 1',
        'endDate': '...',
        'activatedDate': '...',
        'startDate': '...',
        'completeDate': '...',
    }  # Include keys being deleted

    mock_issue = MagicMock()
    mock_issue.key = 'TEST-1'

    mock_jira_client.sprints.return_value = [mock_sprint]
    mock_jira_client.search_issues.return_value = [mock_issue]

    gateway = JiraGateway(mock_jira_client, mock_jira_settings)
    sprints = gateway.find_sprints()

    assert len(sprints) == 1
    assert sprints[0]['id'] == 1
    assert sprints[0]['opened_at'] == datetime(2025, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert sprints[0]['closed_at'] == datetime(2025, 5, 15, 0, 0, tzinfo=timezone.utc)
    assert sprints[0]['team'] == 'TestTeam'
    assert sprints[0]['tickets'] == ['TEST-1']
    mock_jira_client.sprints.assert_called_once()
    mock_jira_client.search_issues.assert_called_once()


def test_jira_gateway_find_sprints_empty(mock_jira_client: MagicMock, mock_jira_settings: MagicMock) -> None:
    """Test finding no sprints."""
    mock_jira_client.sprints.return_value = []

    gateway = JiraGateway(mock_jira_client, mock_jira_settings)
    sprints = gateway.find_sprints()

    assert not sprints
    mock_jira_client.sprints.assert_called_once()
    mock_jira_client.search_issues.assert_not_called()


def test_jira_gateway_find_tickets_success(mock_jira_client: MagicMock, mock_jira_settings: MagicMock) -> None:
    """Test finding tickets successfully."""
    mock_issue = MagicMock(spec=Issue)
    mock_issue.key = 'TEST-2'
    mock_issue.fields = MagicMock()
    mock_issue.fields.resolutiondate = '2025-05-10T00:00:00.000+0000'
    mock_issue.raw = {'key': 'TEST-2', 'fields': {'summary': 'Test Ticket'}}
    mock_issue.changelog = MagicMock()
    mock_issue.changelog.histories = [
        MagicMock(created='2025-05-05T09:00:00.000+0000', items=[MagicMock(field='status', toString='In Progress')]),
        MagicMock(created='2025-05-05T12:00:00.000+0000', items=[MagicMock(field='status', toString='Done')]),
    ]

    mock_jira_client.search_issues.return_value = [mock_issue]

    gateway = JiraGateway(mock_jira_client, mock_jira_settings)
    tickets = gateway.find_tickets(done_at=datetime(2025, 5, 1, tzinfo=timezone.utc))

    assert len(tickets) == 1
    assert tickets[0]['key'] == 'TEST-2'
    assert tickets[0]['team'] == 'TestTeam'
    assert tickets[0]['started_at'] == datetime(2025, 5, 5, 9, 0, tzinfo=tzutc())
    assert tickets[0]['resolved_at'] == datetime(2025, 5, 5, 12, 0, tzinfo=tzutc())
    mock_jira_client.search_issues.assert_called_once()


def test_jira_gateway_find_tickets_no_done_at(mock_jira_client: MagicMock, mock_jira_settings: MagicMock) -> None:
    """Test finding tickets without a done_at filter."""
    mock_issue = MagicMock(spec=Issue)
    mock_issue.key = 'TEST-3'
    mock_issue.fields = MagicMock()
    mock_issue.fields.resolutiondate = '2025-05-12T00:00:00.000+0000'
    mock_issue.raw = {'key': 'TEST-3', 'fields': {'summary': 'Another Ticket'}}
    mock_issue.changelog = MagicMock()
    mock_issue.changelog.histories = [
        MagicMock(created='2025-05-07T10:00:00.000+0000', items=[MagicMock(field='status', toString='In Progress')]),
        MagicMock(created='2025-05-07T11:00:00.000+0000', items=[MagicMock(field='status', toString='Done')]),
    ]

    mock_jira_client.search_issues.return_value = [mock_issue]

    gateway = JiraGateway(mock_jira_client, mock_jira_settings)
    tickets = gateway.find_tickets()

    assert len(tickets) == 1
    mock_jira_client.search_issues.assert_called_once()


def test_jira_gateway_find_tickets_issue_not_started(
    mock_jira_client: MagicMock, mock_jira_settings: MagicMock
) -> None:
    """Test handling of an issue that was never in progress."""
    mock_issue = MagicMock(spec=Issue)
    mock_issue.key = 'TEST-4'
    mock_issue.fields = MagicMock()
    mock_issue.fields.resolutiondate = '2025-05-15T00:00:00.000+0000'
    mock_issue.raw = {'key': 'TEST-4', 'fields': {'summary': 'Never Started'}}
    mock_issue.changelog = MagicMock()
    mock_issue.changelog.histories = [
        MagicMock(created='2025-05-01T08:00:00.000+0000', items=[MagicMock(field='status', toString='Done')])
    ]

    mock_jira_client.search_issues.return_value = [mock_issue]

    gateway = JiraGateway(mock_jira_client, mock_jira_settings)
    tickets = gateway.find_tickets()

    assert not tickets
    mock_jira_client.search_issues.assert_called_once()
