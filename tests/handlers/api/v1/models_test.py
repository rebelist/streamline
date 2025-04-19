import pytest
from pydantic import ValidationError

from streamline.application.compute.models import TimeDataPoint
from streamline.handlers.api.v1.models import TimeSeriesResponse, TimeUnit


class TestTimeUnit:
    """Tests related to the TimeUnit enum and its string values."""

    def test_time_unit_values(self) -> None:
        """Tests the TimeUnit enum values to ensure they match expected string representations."""
        assert TimeUnit.SECONDS.value == 'seconds'
        assert TimeUnit.HOURS.value == 'hours'
        assert TimeUnit.DAYS.value == 'days'
        assert TimeUnit.MINUTES.value == 'minutes'
        assert TimeUnit.NONE.value == 'none'


class TestTimeSeriesResponse:
    """Tests the instantiation and behaviour of the TimeSeriesResponse model, including immutability."""

    def test_time_series_response_model_instantiation(self) -> None:
        """Verify that a TimeSeriesResponse instance is correctly created and enforces frozen config."""
        datapoints = [
            TimeDataPoint(value=2.0, timestamp=1700002000, label='Sprint X'),
            TimeDataPoint(value=5.0, timestamp=1700003000, label='Sprint Y'),
        ]
        response = TimeSeriesResponse(target='cycletime', datapoints=datapoints, unit=TimeUnit.DAYS)

        assert response.target == 'cycletime'
        assert response.datapoints == datapoints
        assert response.type == 'timeseries'
        assert response.unit == TimeUnit.DAYS

        # Test immutability (frozen model)
        with pytest.raises(ValidationError):
            response.target = 'something_else'
