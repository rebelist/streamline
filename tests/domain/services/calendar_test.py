from datetime import datetime, time
from typing import Any

from pytest import fixture
from pytest_mock import MockerFixture

from streamline.domain.services import CalendarService


class TestCalendarService:
    """CalendarService tests."""

    @fixture
    def mock_calendar(self, mocker: MockerFixture) -> Any:
        """Creates a mock calendar with Mon–Fri as working days and fixed day delta."""
        calendar = mocker.Mock()
        calendar.is_working_day.side_effect = lambda d: d.weekday() < 5  # type: ignore[no-any-return]
        calendar.get_working_days_delta.return_value = 3
        return calendar

    @fixture
    def calendar_service(self, mock_calendar: Any) -> CalendarService:
        """Returns a CalendarService instance configured with mocked calendar and 9–17 work hours."""
        return CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)

    def test_get_working_hours_delta_full_days_only(self, calendar_service: CalendarService):
        """Tests the calculation of working hours delta for full working days only."""
        start = datetime(2023, 4, 3, 9, 0)
        end = datetime(2023, 4, 6, 17, 0)
        hours = calendar_service.get_working_hours_delta(start, end)
        assert hours == 24  # 3 full days * 8 hours

    def test_get_working_hours_delta_with_partial_days(self, calendar_service: CalendarService, mock_calendar: Any):
        """Tests the calculation of working hours delta with partial working days."""
        mock_calendar.get_working_days_delta.return_value = 3
        start = datetime(2023, 4, 3, 14, 0)
        end = datetime(2023, 4, 5, 11, 0)
        hours = calendar_service.get_working_hours_delta(start, end)
        assert hours == 13

    def test_get_working_hours_delta_non_working_days(self, calendar_service: CalendarService, mock_calendar: Any):
        """Tests the calculation of working hours delta for a period with no working days."""
        mock_calendar.get_working_days_delta.return_value = 0
        mock_calendar.is_working_day.return_value = False
        start = datetime(2023, 4, 8, 10, 0)
        end = datetime(2023, 4, 9, 15, 0)
        hours = calendar_service.get_working_hours_delta(start, end)
        assert hours == 0
