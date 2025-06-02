from typing import Optional

import pytest
from pydantic_core import ValidationError

from streamline.application.compute.models import CycleTimeDataPoint


class TestCycleTimeDataPoint:
    """Tests for the CycleTimeDataPoint Pydantic model."""

    def test_cycle_time_data_point_creation(self) -> None:
        """Tests the successful creation of a CycleTimeDataPoint instance."""
        data_point = CycleTimeDataPoint(
            duration=5.2, resolved_at=1678886400, key='PROJ-123', sprint='Sprint 1', story_points=1
        )
        assert data_point.duration == 5.2
        assert data_point.resolved_at == 1678886400
        assert data_point.key == 'PROJ-123'
        assert data_point.sprint == 'Sprint 1'

    def test_cycle_time_data_point_immutability(self) -> None:
        """Tests that a CycleTimeDataPoint instance is immutable."""
        data_point = CycleTimeDataPoint(
            duration=3.1, resolved_at=1678972800, key='TASK-456', sprint='Sprint Alpha', story_points=1
        )
        with pytest.raises(ValidationError):
            data_point.duration = 6.7

    def test_cycle_time_data_point_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert CycleTimeDataPoint.model_fields['duration'].description == 'Ticket cycle time'
        assert CycleTimeDataPoint.model_fields['resolved_at'].description == 'Epoch timestamp in seconds'
        assert CycleTimeDataPoint.model_fields['key'].description == 'Ticket identifier'
        assert CycleTimeDataPoint.model_fields['sprint'].description == 'Sprint in which the ticket was started.'
        assert CycleTimeDataPoint.model_fields['story_points'].description == 'Estimated story points.'

    def test_cycle_time_data_point_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert CycleTimeDataPoint.model_fields['duration'].annotation is float
        assert CycleTimeDataPoint.model_fields['resolved_at'].annotation is int
        assert CycleTimeDataPoint.model_fields['key'].annotation is str
        assert CycleTimeDataPoint.model_fields['sprint'].annotation is str
        assert CycleTimeDataPoint.model_fields['story_points'].annotation is Optional[int]
