from typing import Any

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError

from streamline.handlers.api.metrics.models import MetricMetadata, MetricResponse, TimeMetricMetadata, TimeUnit


class DummyDataPoint(BaseModel):
    """Simple dummy class to use as a generic in MetricResponse."""

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

    def test_metric_metadata_instantiation(self) -> None:
        """Test instantiating MetricMetadata with and without optional fields."""
        meta = MetricMetadata(metric='Cycle Time', description='Some description')
        assert meta.metric == 'Cycle Time'
        assert meta.description == 'Some description'

    def test_metric_response_serialization(self) -> None:
        """Test serialization of a MetricResponse with dummy data."""
        datapoints = [DummyDataPoint(value=1), DummyDataPoint(value=2)]
        meta = MetricMetadata(metric='Dummy', description='Test')
        response = MetricResponse[DummyDataPoint, MetricMetadata](datapoints=datapoints, meta=meta)

        assert response.datapoints == datapoints
        assert response.meta.metric == 'Dummy'

    def test_time_metric_response_immutable(self) -> None:
        """Test that MetricResponse is immutable (frozen=True)."""
        response = MetricResponse[DummyDataPoint, MetricMetadata](
            datapoints=[],
            meta=TimeMetricMetadata(metric='ImmutableTest', unit=TimeUnit.NONE, description='Test immutability'),
        )

        # Check if attempting to mutate the response object raises an error
        with pytest.raises(ValidationError):
            response.datapoints = [DummyDataPoint(value=3)]

        # Check if attempting to mutate the `meta` object raises an error
        with pytest.raises(ValidationError):
            response.meta.metric = 'SomethingElse'
