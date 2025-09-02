from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TimeUnit(Enum):
    """Enum representing time units."""

    SECONDS = 'seconds'
    HOURS = 'hours'
    DAYS = 'days'
    MINUTES = 'minutes'
    NONE = 'none'


class MetricMetadata(BaseModel):
    """Metadata describing the metric and its semantic context, including domain dimensions grouping the datapoints."""

    model_config = ConfigDict(frozen=True)

    metric: str = Field(description='Name of the metric')
    description: str = Field(description='Human-readable description of the metric')


class TimeMetricMetadata(MetricMetadata):
    """Metadata for time-indexed datapoints, including the unit of time measurement."""

    unit: TimeUnit = Field(default=TimeUnit.DAYS, description='Unit of the datapoint')


class MetricResponse[T, M: MetricMetadata](BaseModel):
    """Generic response model wrapping a list of datapoints and their associated metric metadata."""

    model_config = ConfigDict(frozen=True)

    datapoints: list[T] = Field(description='List of data points for the metric')
    meta: M = Field(description='Metadata describing the metric and its context')
