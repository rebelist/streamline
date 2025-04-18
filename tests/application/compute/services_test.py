from datetime import datetime, timedelta
from typing import List, Union
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from streamline.application.compute.models import TimeDataPoint
from streamline.application.compute.services import PerformanceService
from streamline.application.compute.use_cases import GetAllSprintCycleTimesUseCase
from streamline.domain.metrics.performance import CycleTime
from streamline.domain.sprint import Sprint


class TestPerformanceService:
    """Unit tests for PerformanceService.

    These tests verify that the service correctly transforms
    cycle time data from the use case layer into time series
    data points.
    """

    def test_get_all_sprint_cycle_times(self, mocker: MockerFixture) -> None:
        """Should return correct list of TimeDataPoint from the cycle time use case."""
        mock_use_case = mocker.Mock(spec=GetAllSprintCycleTimesUseCase)

        mock_sprint: Union[Sprint, Mock] = mocker.Mock()
        mock_sprint.name = 'Sprint Alpha'
        mock_sprint.closed_at = datetime(2025, 4, 18, 12, 0, 0)

        mock_cycle_time: Union[CycleTime, Mock] = Mock()
        mock_cycle_time.sprint = mock_sprint
        mock_cycle_time.duration = timedelta(hours=32)  # 4 workdays (assuming 8h per day)

        mock_use_case.execute.return_value = [mock_cycle_time]

        service: PerformanceService = PerformanceService(cycle_time_use_case=mock_use_case)

        result: List[TimeDataPoint] = service.get_all_sprint_cycle_times()

        assert len(result) == 1
        datapoint = result[0]
        assert datapoint.value == pytest.approx(4.0)  # 32 / 8 = 4
        assert datapoint.timestamp == int(mock_sprint.closed_at.timestamp())
        assert datapoint.label == 'Sprint Alpha'
        mock_use_case.execute.assert_called_once()
