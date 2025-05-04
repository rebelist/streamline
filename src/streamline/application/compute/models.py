from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class CycleTimeDataPoint(BaseModel):
    """Represent a metric data point."""

    model_config = ConfigDict(frozen=True)

    duration: Annotated[float, Field(description='Ticket cycle time')]
    resolved_at: Annotated[int, Field(description='Epoch timestamp in seconds')]
    ticket: Annotated[str, Field(description='Ticket identifier')]
    sprint: Annotated[str, Field(description='Sprint in which the ticket was started.')]
