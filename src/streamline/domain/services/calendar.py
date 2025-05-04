from datetime import date, datetime, time
from typing import Final, Protocol


class WorkCalendarProtocol(Protocol):
    """Protocol for a work calendar."""

    def is_working_day(self, day: date) -> bool:
        """Return True if the given date is a working day."""
        ...

    def get_working_days_delta(self, start: date, end: date) -> int:
        """Return the number of working days between two given dates."""
        ...


class CalendarService:
    """CalendarService service with custom workday configuration."""

    HOUR_IN_SECONDS: Final[int] = 3600

    def __init__(
        self, work_calendar: WorkCalendarProtocol, workday_starts_at: time, workday_ends_at: time, workday_duration: int
    ) -> None:
        """Initializes an object with the given work calendar, workday start time, end time, and workday duration."""
        self.__work_calendar = work_calendar
        self.__workday_starts_at = workday_starts_at
        self.__workday_ends_at = workday_ends_at
        self.__workday_duration = workday_duration

    def get_working_days_delta(self, start_at: datetime, end_at: datetime) -> float:
        """Calculates working hours between two datetimes."""
        start_date = start_at.date()
        end_date = end_at.date()
        working_days = self.__work_calendar.get_working_days_delta(start_date, end_date)
        partial_hours = 0

        # First day
        if self.__is_working_day(start_date):
            partial_hours += self.__calculate_partial_day_hours(start_at, self.__workday_ends_at, is_start=True)
            working_days -= 1

        # Last day
        if self.__is_working_day(end_date) and start_date != end_date:
            partial_hours += self.__calculate_partial_day_hours(end_at, self.__workday_starts_at, is_start=False)
            working_days -= 1

        total_hours = (working_days * self.__workday_duration) + partial_hours
        return round(total_hours / self.__workday_duration, 2)

    def __calculate_partial_day_hours(self, dt: datetime, reference_time: time, is_start: bool) -> float:
        """Calculates worked hours for a partial day."""
        ref_datetime = datetime.combine(dt.date(), reference_time, tzinfo=dt.tzinfo)

        if is_start:
            seconds = max(0.0, (ref_datetime - dt).total_seconds())
        else:
            seconds = max(0.0, (dt - ref_datetime).total_seconds())

        hours = seconds / self.HOUR_IN_SECONDS
        return min(hours, self.__workday_duration)

    def __is_working_day(self, day: date) -> bool:
        """Check if a given date is a work day."""
        return self.__work_calendar.is_working_day(day)
