from typing import List

from pytest_mock import MockerFixture

from streamline.application.compute import FlowMetricsService
from streamline.application.compute.models import CycleTimeDataPoint, LeadTimeDataPoint
from streamline.application.compute.use_cases import GetCycleTimesUseCase
from streamline.application.compute.use_cases.flow import GetLeadTimesUseCase


class TestFlowMetricsService:
    """Tests for the FlowMetricsService class."""

    def test_get_cycle_times_success(self, mocker: MockerFixture) -> None:
        """Tests the successful retrieval of cycle times."""
        mock_cycle_time = mocker.Mock(spec=GetCycleTimesUseCase)
        mock_lead_time = mocker.Mock(spec=GetLeadTimesUseCase)
        expected_data_points: List[CycleTimeDataPoint] = [
            CycleTimeDataPoint(duration=5.0, resolved_at=1683004800, ticket='PROJ-101', sprint='Sprint 1'),
            CycleTimeDataPoint(duration=7.5, resolved_at=1683177600, ticket='PROJ-102', sprint='Sprint 1'),
        ]
        mock_cycle_time.return_value = expected_data_points
        flow_metrics_service = FlowMetricsService(mock_cycle_time, mock_lead_time)
        actual_data_points = flow_metrics_service.get_cycle_times('backend')
        assert actual_data_points == expected_data_points
        mock_cycle_time.assert_called_once()

    def test_get_cycle_times_empty(self, mocker: MockerFixture) -> None:
        """Tests the case where no cycle times are returned."""
        mock_cycle_time = mocker.Mock(spec=GetCycleTimesUseCase)
        mock_lead_time = mocker.Mock(spec=GetLeadTimesUseCase)
        mock_cycle_time.return_value = []
        flow_metrics_service = FlowMetricsService(mock_cycle_time, mock_lead_time)
        actual_data_points = flow_metrics_service.get_cycle_times('frontend')
        assert actual_data_points == []
        mock_cycle_time.assert_called_once()

    def test_get_lead_times_success(self, mocker: MockerFixture) -> None:
        """Tests the successful retrieval of lead times."""
        mock_cycle_time = mocker.Mock(spec=GetCycleTimesUseCase)
        mock_lead_time = mocker.Mock(spec=GetLeadTimesUseCase)
        expected_data_points: List[LeadTimeDataPoint] = [
            LeadTimeDataPoint(duration=5.0, resolved_at=1683004800, ticket='PROJ-101'),
            LeadTimeDataPoint(duration=7.5, resolved_at=1683177600, ticket='PROJ-102'),
        ]
        mock_lead_time.return_value = expected_data_points
        flow_metrics_service = FlowMetricsService(mock_cycle_time, mock_lead_time)
        actual_data_points = flow_metrics_service.get_lead_times('backend')
        assert actual_data_points == expected_data_points
        mock_lead_time.assert_called_once()

    def test_get_lead_times_empty(self, mocker: MockerFixture) -> None:
        """Tests the case where no lead times are returned."""
        mock_cycle_time = mocker.Mock(spec=GetCycleTimesUseCase)
        mock_lead_time = mocker.Mock(spec=GetLeadTimesUseCase)
        mock_lead_time.return_value = []
        flow_metrics_service = FlowMetricsService(mock_cycle_time, mock_lead_time)
        actual_data_points = flow_metrics_service.get_lead_times('frontend')
        assert actual_data_points == []
        mock_lead_time.assert_called_once()
