from datetime import time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from rebelist.streamline.config.settings import AppSettings, JiraSettings, Settings, WorkflowSettings, load_settings


class TestAppSettings:
    """Tests for the AppSettings Pydantic model."""

    def test_app_settings_creation(self: 'TestAppSettings') -> None:
        """Tests the successful creation of an AppSettings instance."""
        settings = AppSettings(country='US', timezone=ZoneInfo('Europe/Berlin'))
        assert settings.name == 'rebelist-streamline'
        assert settings.country == 'US'
        assert settings.timezone == ZoneInfo('Europe/Berlin')

    def test_app_settings_immutability(self: 'TestAppSettings') -> None:
        """Tests that an AppSettings instance is immutable."""
        settings = AppSettings(country='GB', timezone=ZoneInfo('Europe/Berlin'))
        with pytest.raises(ValidationError):
            settings.country = 'NewName'


class TestWorkflowSettings:
    """Tests for the WorkflowSettings Pydantic model."""

    def test_workflow_settings_creation(self: 'TestWorkflowSettings') -> None:
        """Tests the successful creation of a WorkflowSettings instance."""
        settings = WorkflowSettings(workday_starts_at=time(9, 0), workday_ends_at=time(17, 0), workday_duration=8)
        assert settings.workday_starts_at == time(9, 0)
        assert settings.workday_ends_at == time(17, 0)
        assert settings.workday_duration == 8

    def test_workflow_settings_workday_duration_validation(self: 'TestWorkflowSettings') -> None:
        """Tests the validation for workday_duration."""
        with pytest.raises(ValidationError) as excinfo:
            WorkflowSettings(workday_starts_at=time(10, 0), workday_ends_at=time(16, 0), workday_duration=0)
        assert 'workday_duration' in excinfo.value.errors()[0]['loc']
        assert 'greater than 0' in excinfo.value.errors()[0]['msg']

    def test_workflow_settings_immutability(self: 'TestWorkflowSettings') -> None:
        """Tests that a WorkflowSettings instance is immutable."""
        settings = WorkflowSettings(workday_starts_at=time(8, 30), workday_ends_at=time(16, 30), workday_duration=8)
        with pytest.raises(ValidationError):
            settings.workday_starts_at = time(9, 0)


class TestJiraSettings:
    """Tests for the JiraSettings Pydantic model."""

    def test_jira_settings_creation(self: 'TestJiraSettings') -> None:
        """Tests the successful creation of a JiraSettings instance."""
        settings = JiraSettings(
            team='development',
            project='PROJ',
            board_id=123,
            sprint_start_at=100,
            issue_types=['To Do', 'In Progress'],
        )
        assert settings.team == 'Development'
        assert settings.project == 'PROJ'
        assert settings.board_id == 123
        assert settings.sprint_start_at == 100
        assert settings.issue_types == ['To Do', 'In Progress']

    def test_jira_settings_team_capitalization(self: 'TestJiraSettings') -> None:
        """Tests that the 'team' field is automatically capitalized."""
        settings = JiraSettings(
            team='operations', project='OPS', board_id=456, sprint_start_at=200, issue_types=['Open', 'Closed']
        )
        assert settings.team == 'Operations'

    def test_jira_settings_split_issue_statuses_from_list(self: 'TestJiraSettings') -> None:
        """Tests handling issue_statuses when it's already a list."""
        statuses = ['Blocked', 'Review']
        settings = JiraSettings(team='ux', project='UI', board_id=101, sprint_start_at=400, issue_types=statuses)
        assert settings.issue_types == statuses

    def test_jira_settings_immutability(self: 'TestJiraSettings') -> None:
        """Tests that a JiraSettings instance is immutable."""
        settings = JiraSettings(
            team='design', project='DESIGN', board_id=222, sprint_start_at=500, issue_types=['Idea', 'Refinement']
        )
        with pytest.raises(ValidationError):
            settings.project = 'NEW_PROJ'


class TestSettings:
    """Tests for the main Settings Pydantic model."""

    def test_settings_creation(self: 'TestSettings') -> None:
        """Tests the successful creation of a Settings instance."""
        app_settings = AppSettings(country='EU', timezone=ZoneInfo('Europe/Berlin'))
        workflow_settings = WorkflowSettings(
            workday_starts_at=time(8, 0), workday_ends_at=time(16, 0), workday_duration=8
        )
        jira_settings = JiraSettings(
            team='backend', project='BE', board_id=555, sprint_start_at=600, issue_types=['Backlog', 'Dev']
        )
        settings = Settings(app=app_settings, workflow=workflow_settings, jira=jira_settings)
        assert settings.app == app_settings
        assert settings.workflow == workflow_settings
        assert settings.jira == jira_settings

    def test_settings_immutability(self: 'TestSettings') -> None:
        """Tests that a Settings instance is immutable."""
        app_settings = AppSettings(country='US', timezone=ZoneInfo('Europe/Berlin'))
        workflow_settings = WorkflowSettings(
            workday_starts_at=time(9, 0), workday_ends_at=time(18, 0), workday_duration=9
        )
        jira_settings = JiraSettings(
            team='frontend', project='FE', board_id=666, sprint_start_at=700, issue_types=['Planned', 'Coding']
        )
        settings = Settings(app=app_settings, workflow=workflow_settings, jira=jira_settings)
        with pytest.raises(ValidationError):
            settings.app = AppSettings(country='US', timezone=ZoneInfo('Europe/Berlin'))


class TestLoadSettings:
    """Tests for the load_settings function."""

    def test_load_settings_success(self, tmp_path: Path) -> None:
        """Tests loading settings from a valid INI file."""
        config_content = """
        [app]
        country = US
        timezone = Europe/Berlin

        [workflow]
        workday_starts_at = 09:30
        workday_ends_at = 17:30
        workday_duration = 8

        [jira]
        team = analytics
        project = ANALYTICS
        board_id = 999
        sprint_start_at = 800
        issue_types = Open, In Review
        """
        config_file = tmp_path / 'settings.ini'
        config_file.write_text(config_content)

        settings = load_settings(config_file)
        assert settings.app == AppSettings(country='US', timezone=ZoneInfo('Europe/Berlin'))
        assert settings.workflow == WorkflowSettings(
            workday_starts_at=time(9, 30), workday_ends_at=time(17, 30), workday_duration=8
        )
        assert settings.jira == JiraSettings(
            team='Analytics',
            project='ANALYTICS',
            board_id=999,
            sprint_start_at=800,
            issue_types=['Open', 'In Review'],
        )

    def test_load_settings_missing_file(self, tmp_path: Path) -> None:
        """Tests loading settings when the file is missing."""
        missing_file = tmp_path / 'missing.ini'
        with pytest.raises(ValueError, match=f'Failed to read settings file: {missing_file}'):
            load_settings(missing_file)

    def test_load_settings_invalid_format(self, tmp_path: Path) -> None:
        """Tests loading settings from an INI file with invalid format."""
        config_content = """
        [app]
        name = Invalid

        [workflow]
        workday_starts_at = not_a_time
        workday_ends_at = 18:00
        workday_duration = 7

        [jira]
        team = test
        project = INVALID
        board_id = abc
        sprint_start_at = 1000
        issue_types = One
        """
        config_file = tmp_path / 'invalid.ini'
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match='Failed to load settings:'):
            load_settings(config_file)

    def test_load_settings_missing_section(self, tmp_path: Path) -> None:
        """Tests loading settings from an INI file with a missing section."""
        config_content = """
        [app]
        name = PartialApp
        version = 0.1.0
        region = ZZ

        [jira]
        team = partial
        project = PART
        board_id = 111
        sprint_start_at = 900
        issue_types = Yes
        """
        config_file = tmp_path / 'partial.ini'
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match='Failed to load settings:'):
            load_settings(config_file)

    def test_load_settings_missing_field(self, tmp_path: Path) -> None:
        """Tests loading settings from an INI file with a missing field in a section."""
        config_content = """
        [app]
        version = 0.3.0
        region = XY

        [workflow]
        workday_starts_at = 10:00
        workday_ends_at = 18:00
        workday_duration = 8

        [jira]
        team = another
        project = OTHER
        board_id = 222
        sprint_start_at = 1100
        issue_types = Two
        """
        config_file = tmp_path / 'missing_field.ini'
        config_file.write_text(config_content)

        with pytest.raises(ValueError, match='Field required'):
            load_settings(config_file)
