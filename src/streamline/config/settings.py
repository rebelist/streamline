from configparser import ConfigParser
from datetime import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, TypeAdapter, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseModel):
    """Configuration settings for the application metadata."""

    model_config = SettingsConfigDict(frozen=True)

    name: str
    version: str
    region: str


class WorkflowSettings(BaseModel):
    """Configuration settings related to working hours."""

    model_config = SettingsConfigDict(frozen=True)

    workday_starts_at: time
    workday_ends_at: time
    workday_duration: int = Field(gt=0)


class JiraSettings(BaseModel):
    """Configuration settings for Jira integration."""

    model_config = SettingsConfigDict(frozen=True)

    team: str
    project: str
    board_id: int
    sprint_start_at: int
    issue_statuses: list[str]

    @field_validator('team')
    @classmethod
    def capitalized(cls, value: str) -> str:
        """Ensure 'team' is always capitalized."""
        return value.capitalize()

    @field_validator('issue_statuses', mode='before')
    @classmethod
    def split_issue_statuses(cls, value: str | list[str]) -> list[str]:
        """Parses a comma-separated string into a list of statuses."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return value


class Settings(BaseSettings):
    """Main settings class aggregating all configuration sections."""

    model_config = SettingsConfigDict(frozen=True)

    app: AppSettings
    workflow: WorkflowSettings
    jira: JiraSettings


def load_settings(filepath: str | Path) -> Settings:
    """Loads and validates settings from an INI file.

    ValueError: If the file is missing, invalid, or fails validation.
    """
    parser = ConfigParser()

    if not parser.read(filepath):
        raise ValueError(f'Failed to read settings file: {filepath}')

    raw_data: dict[str, Any] = {}
    try:
        for section in parser.sections():
            raw_section: dict[str, Any] = dict(parser.items(section))
            raw_data[section] = raw_section

        adapter = TypeAdapter(Settings)
        settings = adapter.validate_python(raw_data)
        return settings
    except (ValidationError, ValueError, TypeError) as e:
        raise ValueError(f'Failed to load settings: {e}') from e
