from datetime import date, datetime, time, timedelta
from typing import Final, Protocol


class WorkCalendarProtocol(Protocol):
    """Protocol for defining a custom work calendar."""

    def is_working_day(self, day: date) -> bool:
        """Return True if the given date is a working day (e.g., not a weekend or holiday)."""
        ...

    def get_working_days_delta(self, start: date, end: date) -> int:
        """Return the number of working days between two dates, inclusive of start and end."""
        ...


class WorkTimeCalculator:
    """Service to calculate working day durations between two datetimes."""

    HOUR_IN_SECONDS: Final[int] = 3600

    def __init__(
        self,
        work_calendar: WorkCalendarProtocol,
        workday_starts_at: time,
        workday_ends_at: time,
        workday_duration: int,
    ) -> None:
        if workday_starts_at >= workday_ends_at:
            raise ValueError('Workday must start before it ends.')
        if workday_duration <= 0:
            raise ValueError('Workday duration must be positive.')

        self.__work_calendar = work_calendar
        self.__workday_starts_at = workday_starts_at
        self.__workday_ends_at = workday_ends_at
        self.__workday_duration = workday_duration

    def get_working_days_delta(self, start_at: datetime, end_at: datetime) -> float:
        """Calculates the working time between two datetimes as a float number of workdays."""
        if start_at > end_at:
            raise ValueError('start_at must be before end_at.')

        start_date = start_at.date()
        end_date = end_at.date()

        # Handle same day case separately
        if start_date == end_date:
            if self.__is_working_day(start_date):
                work_start = datetime.combine(start_date, self.__workday_starts_at, tzinfo=start_at.tzinfo)
                work_end = datetime.combine(start_date, self.__workday_ends_at, tzinfo=start_at.tzinfo)

                effective_start = max(start_at, work_start)
                effective_end = min(end_at, work_end)

                duration_seconds = max(0.0, (effective_end - effective_start).total_seconds())
                partial_hours = duration_seconds / self.HOUR_IN_SECONDS
                return round(partial_hours / self.__workday_duration, 2)
            else:
                return 0.0

        # Multi-day case
        start_partial = self.__get_partial_hours(start_at, is_start=True) if self.__is_working_day(start_date) else 0.0
        end_partial = self.__get_partial_hours(end_at, is_start=False) if self.__is_working_day(end_date) else 0.0

        # Count full days in between
        in_between_start = start_date + timedelta(days=1)
        in_between_end = end_date - timedelta(days=1)

        if in_between_start <= in_between_end:
            full_days = self.__work_calendar.get_working_days_delta(in_between_start, in_between_end)
        else:
            full_days = 0

        total_hours = (full_days * self.__workday_duration) + start_partial + end_partial
        return round(total_hours / self.__workday_duration, 2)

    def __get_partial_hours(self, target: datetime, is_start: bool) -> float:
        """Calculates the overlap in working hours for a partial day."""
        work_start = datetime.combine(target.date(), self.__workday_starts_at, tzinfo=target.tzinfo)
        work_end = datetime.combine(target.date(), self.__workday_ends_at, tzinfo=target.tzinfo)

        if is_start:
            if target >= work_end:
                return 0.0
            effective_start = max(target, work_start)
            effective_end = work_end
        else:
            if target <= work_start:
                return 0.0
            effective_start = work_start
            effective_end = min(target, work_end)

        seconds = max(0.0, (effective_end - effective_start).total_seconds())
        hours = seconds / self.HOUR_IN_SECONDS
        return min(hours, self.__workday_duration)

    def __is_working_day(self, day: date) -> bool:
        """Check if a given date is a workday according to the calendar."""
        return self.__work_calendar.is_working_day(day)
