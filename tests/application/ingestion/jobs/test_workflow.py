from datetime import datetime, timezone

from pytest_mock import MockerFixture

from streamline.application.ingestion.jobs import SprintJob, TicketJob
from streamline.config.settings import JiraSettings
from streamline.infrastructure.jira.gateway import JiraGateway
from streamline.infrastructure.mongo.job.repositories import Job, JobRepository
from streamline.infrastructure.mongo.sprint import MongoSprintDocumentRepository
from streamline.infrastructure.mongo.ticket import MongoTicketDocumentRepository


class TestSprintJob:
    """Tests for the SprintJob class."""

    def test_execute_new_job(self, mocker: MockerFixture) -> None:
        """Tests the execute method when no previous job exists."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_sprint_repo = mocker.Mock(spec=MongoSprintDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)

        mock_settings.team = 'test_team'
        mock_settings.sprint_start_at = 100
        mock_jira_gateway.find_sprints.return_value = [
            {
                'id': '1',
                'name': 'Sprint 1',
                'start_date': datetime.now(timezone.utc),
                'end_date': datetime.now(timezone.utc),
            },
            {
                'id': '2',
                'name': 'Sprint 2',
                'start_date': datetime.now(timezone.utc),
                'end_date': datetime.now(timezone.utc),
            },
        ]
        mock_job_repo.find.return_value = None
        mock_job_repo.save.return_value = None

        job = SprintJob(mock_jira_gateway, mock_sprint_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(SprintJob.JOB_NAME, 'test_team')
        mock_jira_gateway.find_sprints.assert_called_once_with(100)
        assert mock_sprint_repo.save.call_count == 2
        mock_job_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.name == SprintJob.JOB_NAME
        assert saved_job.team == 'test_team'
        assert saved_job.metadata == {'sprint_index_start_at': 102}
        assert saved_job.executed_at is not None

    def test_execute_existing_job(self, mocker: MockerFixture) -> None:
        """Tests the execute method when a previous job exists."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_sprint_repo = mocker.Mock(spec=MongoSprintDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)
        mock_existing_job = mocker.Mock(spec=Job)

        mock_settings.team = 'another_team'
        mock_settings.sprint_start_at = 50
        mock_existing_job.metadata = {'sprint_index_start_at': 105}
        mock_jira_gateway.find_sprints.return_value = [
            {
                'id': '3',
                'name': 'Sprint 3',
                'start_date': datetime.now(timezone.utc),
                'end_date': datetime.now(timezone.utc),
            },
        ]
        mock_job_repo.find.return_value = mock_existing_job
        mock_job_repo.save.return_value = None

        job = SprintJob(mock_jira_gateway, mock_sprint_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(SprintJob.JOB_NAME, 'another_team')
        mock_jira_gateway.find_sprints.assert_called_once_with(105)
        mock_sprint_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.metadata == {'sprint_index_start_at': 106}
        assert saved_job.executed_at is not None

    def test_execute_no_new_sprints(self, mocker: MockerFixture) -> None:
        """Tests the execute method when no new sprints are found."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_sprint_repo = mocker.Mock(spec=MongoSprintDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)
        mock_existing_job = mocker.Mock(spec=Job)

        mock_settings.team = 'yet_another_team'
        mock_settings.sprint_start_at = 200
        mock_existing_job.metadata = {'sprint_index_start_at': 200}
        mock_jira_gateway.find_sprints.return_value = []
        mock_job_repo.find.return_value = mock_existing_job
        mock_job_repo.save.return_value = None

        job = SprintJob(mock_jira_gateway, mock_sprint_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(SprintJob.JOB_NAME, 'yet_another_team')
        mock_jira_gateway.find_sprints.assert_called_once_with(200)
        mock_sprint_repo.save.assert_not_called()
        mock_job_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.metadata == {'sprint_index_start_at': 200}
        assert saved_job.executed_at is not None


class TestTicketJob:
    """Tests for the TicketJob class."""

    def test_execute_new_job(self, mocker: MockerFixture) -> None:
        """Tests the execute method when no previous ticket job exists."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_ticket_repo = mocker.Mock(spec=MongoTicketDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)
        mock_now = datetime.now(timezone.utc)

        mock_settings.team = 'alpha_team'
        mock_jira_gateway.find_tickets.return_value = [
            {'id': 'TKT-1', 'title': 'Ticket One', 'done_at': mock_now},
            {'id': 'TKT-2', 'title': 'Ticket Two', 'done_at': mock_now},
        ]
        mock_job_repo.find.return_value = None
        mock_job_repo.save.return_value = None
        mocker.patch(
            'streamline.application.ingestion.jobs.workflow.datetime',
            mocker.Mock(now=mocker.Mock(return_value=mock_now)),
        )

        job = TicketJob(mock_jira_gateway, mock_ticket_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(TicketJob.JOB_NAME, 'alpha_team')
        mock_jira_gateway.find_tickets.assert_called_once_with(None)
        assert mock_ticket_repo.save.call_count == 2
        mock_job_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.name == TicketJob.JOB_NAME
        assert saved_job.team == 'alpha_team'
        assert saved_job.metadata == {'tickets_done_at': mock_now}
        assert saved_job.executed_at == mock_now

    def test_execute_existing_job(self, mocker: MockerFixture) -> None:
        """Tests the execute method when a previous ticket job exists."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_ticket_repo = mocker.Mock(spec=MongoTicketDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)
        mock_existing_job = mocker.Mock(spec=Job)
        previous_done_at = datetime(2025, 5, 4, 10, 0, 0, tzinfo=timezone.utc)
        mock_now = datetime.now(timezone.utc)

        mock_settings.team = 'beta_team'
        mock_existing_job.metadata = {'tickets_done_at': previous_done_at}
        mock_jira_gateway.find_tickets.return_value = [
            {'id': 'TKT-3', 'title': 'Ticket Three', 'done_at': mock_now},
        ]
        mock_job_repo.find.return_value = mock_existing_job
        mock_job_repo.save.return_value = None
        mocker.patch(
            'streamline.application.ingestion.jobs.workflow.datetime',
            mocker.Mock(now=mocker.Mock(return_value=mock_now)),
        )

        job = TicketJob(mock_jira_gateway, mock_ticket_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(TicketJob.JOB_NAME, 'beta_team')
        mock_jira_gateway.find_tickets.assert_called_once_with(previous_done_at)
        mock_ticket_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.metadata == {'tickets_done_at': mock_now}
        assert saved_job.executed_at == mock_now

    def test_execute_no_new_tickets(self, mocker: MockerFixture) -> None:
        """Tests the execute method when no new tickets are found."""
        mock_jira_gateway = mocker.Mock(spec=JiraGateway)
        mock_ticket_repo = mocker.Mock(spec=MongoTicketDocumentRepository)
        mock_job_repo = mocker.Mock(spec=JobRepository)
        mock_settings = mocker.Mock(spec=JiraSettings)
        mock_existing_job = mocker.Mock(spec=Job)
        previous_done_at = datetime(2025, 5, 4, 9, 0, 0, tzinfo=timezone.utc)
        mock_now = datetime.now(timezone.utc)

        mock_settings.team = 'gamma_team'
        mock_existing_job.metadata = {'tickets_done_at': previous_done_at}
        mock_jira_gateway.find_tickets.return_value = []
        mock_job_repo.find.return_value = mock_existing_job
        mock_job_repo.save.return_value = None
        mocker.patch(
            'streamline.application.ingestion.jobs.workflow.datetime',
            mocker.Mock(now=mocker.Mock(return_value=mock_now)),
        )

        job = TicketJob(mock_jira_gateway, mock_ticket_repo, mock_job_repo, mock_settings)
        job.execute()

        mock_job_repo.find.assert_called_once_with(TicketJob.JOB_NAME, 'gamma_team')
        mock_jira_gateway.find_tickets.assert_called_once_with(previous_done_at)
        mock_ticket_repo.save.assert_not_called()
        mock_job_repo.save.assert_called_once()
        saved_job: Job = mock_job_repo.save.call_args[0][0]
        assert saved_job.metadata == {'tickets_done_at': mock_now}
        assert saved_job.executed_at == mock_now
