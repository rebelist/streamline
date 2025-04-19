from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from streamline.application.compute.models import TimeDataPoint


class TimeUnit(Enum):
    """Enum representing time units."""

    SECONDS = 'seconds'
    HOURS = 'hours'
    DAYS = 'days'
    MINUTES = 'minutes'
    NONE = 'none'


class TimeSeriesResponse(BaseModel):
    """Response model for an API endpoint that returns time series data n a format suitable for Grafana."""

    target: str = Field(description='Target metric name')
    datapoints: List[TimeDataPoint] = Field(description='List of data points for the time series')
    type: str = Field(default='timeseries', description="Type of data ('timeseries' or 'table')")
    unit: TimeUnit = Field(default=TimeUnit.HOURS, description='Unit of the data')

    model_config = ConfigDict(frozen=True)
