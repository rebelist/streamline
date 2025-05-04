from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar('T')


class TimeUnit(Enum):
    """Enum representing time units."""

    SECONDS = 'seconds'
    HOURS = 'hours'
    DAYS = 'days'
    MINUTES = 'minutes'
    NONE = 'none'


class TimeSeriesMetadata(BaseModel):
    """Metadata for a time series metric."""

    metric: str = Field(description='Name of the metric')
    unit: TimeUnit = Field(default=TimeUnit.DAYS, description='Unit of the datapoint')
    description: str = Field(description='Human-readable description of the metric')


class TimeSeriesResponse(BaseModel, Generic[T]):
    """Generic response model for time series data in a format suitable for Grafana."""

    datapoints: list[T] = Field(description='List of data points for the time series')
    meta: TimeSeriesMetadata = Field(description='Additional metadata about the response')

    model_config = {'frozen': True}
