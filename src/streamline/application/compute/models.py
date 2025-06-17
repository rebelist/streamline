from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class CycleTimeDataPoint(BaseModel):
    """Represents a cycle time data point."""

    model_config = ConfigDict(frozen=True)

    duration: Annotated[float, Field(description='Time taken to complete the ticket (in days).')]
    resolved_at: Annotated[int, Field(description='Epoch timestamp (in seconds) when the ticket was resolved.')]
    key: Annotated[str, Field(description='Unique identifier of the ticket.')]
    sprint: Annotated[str, Field(description='Sprint in which the ticket work started.')]
    story_points: Annotated[Optional[int], Field(description='Estimated story points assigned to the ticket.')]


class LeadTimeDataPoint(BaseModel):
    """Represents a lead time data point."""

    model_config = ConfigDict(frozen=True)

    duration: Annotated[float, Field(description='Time from ticket creation to completion (in days).')]
    resolved_at: Annotated[int, Field(description='Epoch timestamp (in seconds) when the ticket was resolved.')]
    key: Annotated[str, Field(description='Unique identifier of the ticket.')]
    story_points: Annotated[Optional[int], Field(description='Estimated story points assigned to the ticket.')]


class ThroughputDataPoint(BaseModel):
    """Represents a throughput data point for a sprint."""

    model_config = ConfigDict(frozen=True)

    sprint: Annotated[str, Field(description='Name of the sprint.')]
    completed: Annotated[int, Field(description='Number of tickets completed during the sprint.')]
    closed_at: Annotated[int, Field(description='Epoch timestamp (in seconds) when the sprint was closed.')]
    residuals: Annotated[int, Field(description='Number of tickets not completed by the end of the sprint.')]
