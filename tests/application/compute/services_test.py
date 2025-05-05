from typing import List

from pytest_mock import MockerFixture

from streamline.application.compute import PerformanceService
from streamline.application.compute.models import CycleTimeDataPoint
from streamline.application.compute.use_cases import GetCycleTimesUseCase


class TestPerformanceService:
    """Tests for the PerformanceService class."""

    def test_get_cycle_times_success(self, mocker: MockerFixture) -> None:
        """Tests the successful retrieval of cycle times."""
        mock_use_case = mocker.Mock(spec=GetCycleTimesUseCase)
        expected_data_points: List[CycleTimeDataPoint] = [
            CycleTimeDataPoint(duration=5.0, resolved_at=1683004800, ticket='PROJ-101', sprint='Sprint 1'),
            CycleTimeDataPoint(duration=7.5, resolved_at=1683177600, ticket='PROJ-102', sprint='Sprint 1'),
        ]
        mock_use_case.return_value = expected_data_points
        performance_service = PerformanceService(mock_use_case)
        actual_data_points = performance_service.get_cycle_times('backend')
        assert actual_data_points == expected_data_points
        mock_use_case.assert_called_once()

    def test_get_cycle_times_empty(self, mocker: MockerFixture) -> None:
        """Tests the case where no cycle times are returned."""
        mock_use_case = mocker.Mock(spec=GetCycleTimesUseCase)
        mock_use_case.return_value = []
        performance_service = PerformanceService(mock_use_case)
        actual_data_points = performance_service.get_cycle_times('frontend')
        assert actual_data_points == []
        mock_use_case.assert_called_once()
