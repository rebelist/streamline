from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class CycleTimeDataPoint(BaseModel):
    """Represent a cycle time data point."""

    model_config = ConfigDict(frozen=True)

    duration: Annotated[float, Field(description='Ticket cycle time')]
    resolved_at: Annotated[int, Field(description='Epoch timestamp in seconds')]
    key: Annotated[str, Field(description='Ticket identifier')]
    sprint: Annotated[str, Field(description='Sprint in which the ticket was started.')]
    story_points: Annotated[Optional[int], Field(description='Estimated story points.')]


class LeadTimeDataPoint(BaseModel):
    """Represent a lead time data point."""

    model_config = ConfigDict(frozen=True)

    duration: Annotated[float, Field(description='Ticket cycle time')]
    resolved_at: Annotated[int, Field(description='Epoch timestamp in seconds')]
    key: Annotated[str, Field(description='Ticket identifier')]
    story_points: Annotated[Optional[int], Field(description='Estimated story points.')]
