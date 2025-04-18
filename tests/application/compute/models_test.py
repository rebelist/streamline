from pydantic import ValidationError
from pytest import raises

from streamline.application.compute import TimeDataPoint


class TestTimeDataPoint:
    """Test for TimeDataPoint."""

    def test_time_data_point_creation(self) -> None:
        """Test the creation of a TimeDataPoint object with valid data."""
        data_point = TimeDataPoint(value=100.5, timestamp=1618033988749, label='metric1')

        assert data_point.value == 100.5
        assert data_point.timestamp == 1618033988749
        assert data_point.label == 'metric1'

    def test_time_data_point_frozen(self) -> None:
        """Test that TimeDataPoint is frozen and cannot be modified."""
        data_point = TimeDataPoint(value=100.5, timestamp=1618033988749, label='metric1')

        # Act and Assert
        with raises(ValidationError):
            data_point.value = 200.5

        with raises(ValidationError):
            data_point.timestamp = 1628033988749

        with raises(ValidationError):
            data_point.label = 'metric2'
