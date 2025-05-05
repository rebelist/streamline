from typing import Any

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError

from streamline.handlers.api.v1.models import TimeSeriesMetadata, TimeSeriesResponse, TimeUnit


class DummyDataPoint(BaseModel):
    """Simple dummy class to use as a generic in TimeSeriesResponse."""

    value: Any


class TestTimeSeriesModels:
    """Unit tests for the time series metric models."""

    def test_time_unit_enum_values(self) -> None:
        """Test the values of the TimeUnit enum."""
        assert TimeUnit.SECONDS.value == 'seconds'
        assert TimeUnit.HOURS.value == 'hours'
        assert TimeUnit.DAYS.value == 'days'
        assert TimeUnit.MINUTES.value == 'minutes'
        assert TimeUnit.NONE.value == 'none'

    def test_time_series_metadata_instantiation(self) -> None:
        """Test instantiating TimeSeriesMetadata with and without optional fields."""
        meta = TimeSeriesMetadata(metric='Cycle Time', unit=TimeUnit.HOURS, description='Some description')
        assert meta.metric == 'Cycle Time'
        assert meta.unit == TimeUnit.HOURS
        assert meta.description == 'Some description'

    def test_time_series_metadata_default_unit(self) -> None:
        """Test that TimeSeriesMetadata uses TimeUnit.DAYS as default."""
        meta = TimeSeriesMetadata(metric='Lead Time', description='Test metric')
        assert meta.unit == TimeUnit.DAYS

    def test_time_series_response_serialization(self) -> None:
        """Test serialization of a TimeSeriesResponse with dummy data."""
        datapoints = [DummyDataPoint(value=1), DummyDataPoint(value=2)]
        meta = TimeSeriesMetadata(metric='Dummy', unit=TimeUnit.SECONDS, description='Test')
        response = TimeSeriesResponse[DummyDataPoint](datapoints=datapoints, meta=meta)

        assert response.datapoints == datapoints
        assert response.meta.metric == 'Dummy'

    def test_time_series_response_immutable(self) -> None:
        """Test that TimeSeriesResponse is immutable (frozen=True)."""
        response = TimeSeriesResponse[DummyDataPoint](
            datapoints=[],
            meta=TimeSeriesMetadata(metric='ImmutableTest', unit=TimeUnit.NONE, description='Test immutability'),
        )

        # Check if attempting to mutate the response object raises an error
        with pytest.raises(ValidationError):
            response.datapoints = [DummyDataPoint(value=3)]  # Trying to change the datapoints list

        # Check if attempting to mutate the `meta` object raises an error
        with pytest.raises(ValidationError):
            response.meta.metric = 'SomethingElse'
