from typing import Optional

import pytest
from pydantic_core import ValidationError

from streamline.application.compute.models import (
    CycleTimeDataPoint,
    LeadTimeDataPoint,
    SprintCycleTimeDataPoint,
    ThroughputDataPoint,
    VelocityDataPoint,
)


class TestCycleTimeSprintDataPoint:
    """Tests for the SprintCycleTimeDataPoint Pydantic model."""

    def test_cycle_time_data_point_creation(self) -> None:
        """Tests the successful creation of a SprintCycleTimeDataPoint instance."""
        data_point = SprintCycleTimeDataPoint(
            duration=5.2,
            resolved_at=1678886400,
            key='PROJ-123',
            sprint='Sprint 1',
        )
        assert data_point.duration == 5.2
        assert data_point.resolved_at == 1678886400
        assert data_point.key == 'PROJ-123'
        assert data_point.sprint == 'Sprint 1'

    def test_cycle_time_data_point_immutability(self) -> None:
        """Tests that a SprintCycleTimeDataPoint instance is immutable."""
        data_point = SprintCycleTimeDataPoint(
            duration=3.1,
            resolved_at=1678972800,
            key='TASK-456',
            sprint='Sprint Alpha',
        )
        with pytest.raises(ValidationError):
            data_point.duration = 6.7

    def test_cycle_time_data_point_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert (
            SprintCycleTimeDataPoint.model_fields['duration'].description
            == 'Time taken to complete the ticket (in days).'
        )
        assert (
            SprintCycleTimeDataPoint.model_fields['resolved_at'].description
            == 'Epoch timestamp (in seconds) when the ticket was resolved.'
        )
        assert SprintCycleTimeDataPoint.model_fields['key'].description == 'Unique identifier of the ticket.'
        assert SprintCycleTimeDataPoint.model_fields['sprint'].description == 'Sprint in which the ticket work started.'

    def test_cycle_time_data_point_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert SprintCycleTimeDataPoint.model_fields['duration'].annotation is float
        assert SprintCycleTimeDataPoint.model_fields['resolved_at'].annotation is int
        assert SprintCycleTimeDataPoint.model_fields['key'].annotation is str
        assert SprintCycleTimeDataPoint.model_fields['sprint'].annotation is str


class TestCycleTimeDataPoint:
    """Tests for the CycleTimeDataPoint Pydantic model."""

    def test_creation(self) -> None:
        """Tests the successful creation of a CycleTimeDataPoint instance."""
        data_point = CycleTimeDataPoint(duration=2.4, resolved_at=1679000000, key='BUG-789', story_points=3)
        assert data_point.duration == 2.4
        assert data_point.resolved_at == 1679000000
        assert data_point.key == 'BUG-789'
        assert data_point.story_points == 3

    def test_immutability(self) -> None:
        """Tests that a CycleTimeDataPoint instance is immutable."""
        data_point = CycleTimeDataPoint(duration=4.5, resolved_at=1679100000, key='TICKET-001', story_points=2)
        with pytest.raises(ValidationError):
            data_point.key = 'TICKET-CHANGED'

    def test_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert CycleTimeDataPoint.model_fields['duration'].description == 'Time taken to complete the ticket (in days).'
        assert (
            CycleTimeDataPoint.model_fields['resolved_at'].description
            == 'Epoch timestamp (in seconds) when the ticket was resolved.'
        )
        assert CycleTimeDataPoint.model_fields['key'].description == 'Unique identifier of the ticket.'
        assert (
            CycleTimeDataPoint.model_fields['story_points'].description
            == 'Estimated story points assigned to the ticket.'
        )

    def test_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert CycleTimeDataPoint.model_fields['duration'].annotation is float
        assert CycleTimeDataPoint.model_fields['resolved_at'].annotation is int
        assert CycleTimeDataPoint.model_fields['key'].annotation is str
        assert CycleTimeDataPoint.model_fields['story_points'].annotation is Optional[int]


class TestLeadTimeDataPoint:
    """Tests for the LeadTimeDataPoint Pydantic model."""

    def test_creation(self) -> None:
        """Tests the successful creation of a LeadTimeDataPoint instance."""
        data_point = LeadTimeDataPoint(duration=7.0, resolved_at=1679200000, key='FEAT-234', story_points=5)
        assert data_point.duration == 7.0
        assert data_point.resolved_at == 1679200000
        assert data_point.key == 'FEAT-234'
        assert data_point.story_points == 5

    def test_immutability(self) -> None:
        """Tests that a LeadTimeDataPoint instance is immutable."""
        data_point = LeadTimeDataPoint(duration=6.2, resolved_at=1679300000, key='TASK-002', story_points=1)
        with pytest.raises(ValidationError):
            data_point.story_points = 8

    def test_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert (
            LeadTimeDataPoint.model_fields['duration'].description
            == 'Time from ticket creation to completion (in days).'
        )
        assert (
            LeadTimeDataPoint.model_fields['resolved_at'].description
            == 'Epoch timestamp (in seconds) when the ticket was resolved.'
        )
        assert LeadTimeDataPoint.model_fields['key'].description == 'Unique identifier of the ticket.'
        assert (
            LeadTimeDataPoint.model_fields['story_points'].description
            == 'Estimated story points assigned to the ticket.'
        )

    def test_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert LeadTimeDataPoint.model_fields['duration'].annotation is float
        assert LeadTimeDataPoint.model_fields['resolved_at'].annotation is int
        assert LeadTimeDataPoint.model_fields['key'].annotation is str
        assert LeadTimeDataPoint.model_fields['story_points'].annotation is Optional[int]


class TestThroughputDataPoint:
    """Tests for the ThroughputDataPoint Pydantic model."""

    def test_creation(self) -> None:
        """Tests the successful creation of a ThroughputDataPoint instance."""
        data_point = ThroughputDataPoint(sprint='Sprint 2', completed=12, residuals=3)
        assert data_point.sprint == 'Sprint 2'
        assert data_point.completed == 12
        assert data_point.residuals == 3

    def test_immutability(self) -> None:
        """Tests that a ThroughputDataPoint instance is immutable."""
        data_point = ThroughputDataPoint(sprint='Sprint X', completed=7, residuals=1)
        with pytest.raises(ValidationError):
            data_point.completed = 9

    def test_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert ThroughputDataPoint.model_fields['sprint'].description == 'Name of the sprint.'
        assert (
            ThroughputDataPoint.model_fields['completed'].description
            == 'Number of tickets completed during the sprint.'
        )
        assert (
            ThroughputDataPoint.model_fields['residuals'].description
            == 'Number of tickets not completed by the end of the sprint.'
        )

    def test_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert ThroughputDataPoint.model_fields['sprint'].annotation is str
        assert ThroughputDataPoint.model_fields['completed'].annotation is int
        assert ThroughputDataPoint.model_fields['residuals'].annotation is int


class TestVelocityDataPoint:
    """Tests for the VelocityDataPoint Pydantic model."""

    def test_creation(self) -> None:
        """Tests the successful creation of a VelocityDataPoint instance."""
        data_point = VelocityDataPoint(sprint='Sprint 3', story_points_residual=5, story_points_completed=20)
        assert data_point.sprint == 'Sprint 3'
        assert data_point.story_points_residual == 5
        assert data_point.story_points_completed == 20

    def test_immutability(self) -> None:
        """Tests that a VelocityDataPoint instance is immutable."""
        data_point = VelocityDataPoint(sprint='Sprint Z', story_points_residual=0, story_points_completed=15)
        with pytest.raises(ValidationError):
            data_point.sprint = 'Sprint Modified'

    def test_field_descriptions(self) -> None:
        """Tests that the field descriptions are correctly defined."""
        assert VelocityDataPoint.model_fields['sprint'].description == 'Name of the sprint.'
        assert (
            VelocityDataPoint.model_fields['story_points_residual'].description
            == 'Number of story points not completed in the sprint.'
        )
        assert (
            VelocityDataPoint.model_fields['story_points_completed'].description
            == 'Number of story points completed during the sprint.'
        )

    def test_type_hints(self) -> None:
        """Tests that the type hints for the fields are correctly defined."""
        assert VelocityDataPoint.model_fields['sprint'].annotation is str
        assert VelocityDataPoint.model_fields['story_points_residual'].annotation is int
        assert VelocityDataPoint.model_fields['story_points_completed'].annotation is int
