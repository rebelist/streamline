from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TimeDataPoint(BaseModel):
    """Represent a metric data point."""

    model_config = ConfigDict(frozen=True)

    value: Annotated[float, Field(description='Data point value')]
    timestamp: Annotated[int, Field(description='Epoch timestamp in milliseconds')]
    label: Annotated[str, Field(description='Data point identifier')]
