from typing import List

from pytest_mock import MockerFixture

from streamline.application.compute.use_cases import GetAllSprintCycleTimesUseCase
from streamline.domain.metrics.performance import CycleTime
from streamline.domain.sprint import Sprint


class TestGetAllSprintCycleTimesUseCase:
    """Test cases for GetAllSprintCycleTimesUseCase class."""

    def test_execute_should_return_cycle_times_for_all_sprints(self, mocker: MockerFixture) -> None:
        """Should compute cycle time for each sprint using the calculator."""
        mock_calculator = mocker.Mock()
        mock_repository = mocker.Mock()

        # Create fake sprints
        fake_sprints: List[Sprint] = [mocker.Mock(name='Sprint1'), mocker.Mock(name='Sprint2')]
        mock_repository.find_sprints.return_value = fake_sprints

        # Create fake cycle times (one per sprint)
        fake_cycle_times: List[CycleTime] = [mocker.Mock(name='CycleTime1'), mocker.Mock(name='CycleTime2')]
        mock_calculator.calculate.side_effect = fake_cycle_times  # returns one for each call

        use_case = GetAllSprintCycleTimesUseCase(mock_calculator, mock_repository)
        result: List[CycleTime] = use_case.execute()

        assert result == fake_cycle_times
        mock_repository.find_sprints.assert_called_once()
        assert mock_calculator.calculate.call_count == len(fake_sprints)
        for sprint in fake_sprints:
            mock_calculator.calculate.assert_any_call(sprint)
