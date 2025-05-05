from datetime import date, datetime, time, timedelta, timezone

import pytest
from pytest_mock import MockerFixture

from streamline.domain.services import CalendarService, WorkCalendarProtocol


class MockWorkCalendar:
    """A mock implementation of the WorkCalendarProtocol for testing."""

    def __init__(self, working_days: list[date]) -> None:
        self.working_days = working_days

    def is_working_day(self, day: date) -> bool:
        """Check if is working day."""
        return day in self.working_days

    def get_working_days_delta(self, start: date, end: date) -> int:
        """Calculate the number of working days between two dates."""
        count = 0
        current = start
        while current <= end:
            if self.is_working_day(current):
                count += 1
            current += timedelta(days=1)
        return count


class TestCalendarService:
    """Tests for the CalendarService class."""

    def test_initialization_valid_inputs(self, mocker: MockerFixture) -> None:
        """Tests initialization with valid workday start, end, and duration."""
        mock_calendar = mocker.Mock(spec=WorkCalendarProtocol)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        assert service is not None

    def test_initialization_invalid_workday_hours(self, mocker: MockerFixture) -> None:
        """Tests initialization when workday starts after or at the same time as it ends."""
        mock_calendar = mocker.Mock(spec=WorkCalendarProtocol)
        with pytest.raises(ValueError, match='Workday must start before it ends.'):
            CalendarService(mock_calendar, time(17, 0), time(9, 0), 8)
        with pytest.raises(ValueError, match='Workday must start before it ends.'):
            CalendarService(mock_calendar, time(9, 0), time(9, 0), 8)

    def test_initialization_invalid_workday_duration(self, mocker: MockerFixture) -> None:
        """Tests initialization when workday duration is not positive."""
        mock_calendar = mocker.Mock(spec=WorkCalendarProtocol)
        with pytest.raises(ValueError, match='Workday duration must be positive.'):
            CalendarService(mock_calendar, time(9, 0), time(17, 0), 0)
        with pytest.raises(ValueError, match='Workday duration must be positive.'):
            CalendarService(mock_calendar, time(9, 0), time(17, 0), -1)

    def test_get_working_days_delta_same_working_day_within_hours(
        self,
    ) -> None:
        """Tests delta calculation for the same working day within working hours."""
        working_days = [date(2025, 5, 5)]  # Monday
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 5, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 0.25  # 2 hours / 8 hours per day

    def test_get_working_days_delta_same_working_day_partial_overlap_start(
        self,
    ) -> None:
        """Tests delta calculation for the same working day with partial overlap at the start."""
        working_days = [date(2025, 5, 6)]  # Tuesday
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 6, 8, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 6, 10, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 0.12  # 1 hour (9-10) / 8 hours per day, rounded

    def test_get_working_days_delta_same_working_day_partial_overlap_end(
        self,
    ) -> None:
        """Tests delta calculation for the same working day with partial overlap at the end."""
        working_days = [date(2025, 5, 7)]  # Wednesday
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 7, 15, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 7, 18, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 0.25  # 2 hours (15-17) / 8 hours per day

    def test_get_working_days_delta_same_non_working_day(
        self,
    ) -> None:
        """Tests delta calculation for the same non-working day."""
        working_days = [date(2025, 5, 8)]  # Thursday
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 9, 10, 0, 0, tzinfo=timezone.utc)  # Friday (assuming non-working)
        end = datetime(2025, 5, 9, 12, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 0.0

    def test_get_working_days_delta_multi_day_all_working(
        self,
    ) -> None:
        """Tests delta calculation across multiple working days."""
        working_days = [date(2025, 5, 12), date(2025, 5, 13), date(2025, 5, 14)]  # Mon, Tue, Wed
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 12, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 14, 16, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 2.75  # 2 full days + 2 hours (Mon) + 7 hours (Wed) / 8

    def test_get_working_days_delta_multi_day_with_non_working(
        self,
    ) -> None:
        """Tests delta calculation across multiple days including non-working days."""
        working_days = [date(2025, 5, 15), date(2025, 5, 16), date(2025, 5, 19)]  # Thu, Fri, Mon (skipping weekend)
        mock_calendar = MockWorkCalendar(working_days)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 15, 9, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 19, 17, 0, 0, tzinfo=timezone.utc)
        delta = service.get_working_days_delta(start, end)
        assert delta == 3.0  # 8h (Thu) + 8h (Fri) + 8h (Mon) / 8

    def test_get_working_days_delta_start_after_end_raises_error(self, mocker: MockerFixture) -> None:
        """Tests that ValueError is raised when start_at is after end_at."""
        mock_calendar = mocker.Mock(spec=WorkCalendarProtocol)
        service = CalendarService(mock_calendar, time(9, 0), time(17, 0), 8)
        start = datetime(2025, 5, 20, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 5, 20, 9, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match='start_at must be before end_at.'):
            service.get_working_days_delta(start, end)
