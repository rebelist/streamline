from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from rebelist.streamline.infrastructure.datetime import DateTimeNormalizer


class TestDateTimeNormalizer:
    """Test suite for the DateTimeNormalizer service class."""

    def setup_method(self) -> None:
        """Initialize a DateTimeNormalizer instance with Europe/Berlin timezone."""
        self.normalizer = DateTimeNormalizer(ZoneInfo('Europe/Berlin'))

    def test_normalize_naive_datetime_assumes_utc(self) -> None:
        """Normalize naive datetime as UTC to target timezone."""
        naive_dt = datetime(2024, 5, 10, 12, 0, 0)  # naive datetime (assumed UTC)
        normalized = self.normalizer.normalize(naive_dt)

        # Expect tzinfo to be Europe/Berlin
        assert normalized.tzinfo == ZoneInfo('Europe/Berlin')
        # The normalized time should be UTC+2 or UTC+1 depending on DST
        expected_dt = naive_dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo('Europe/Berlin'))
        assert normalized == expected_dt

    def test_normalize_aware_datetime(self) -> None:
        """Normalize aware datetime to target timezone."""
        aware_dt = datetime(2024, 5, 10, 12, 0, 0, tzinfo=ZoneInfo('UTC'))
        normalized = self.normalizer.normalize(aware_dt)

        assert normalized.tzinfo == ZoneInfo('Europe/Berlin')
        expected_dt = aware_dt.astimezone(ZoneInfo('Europe/Berlin'))
        assert normalized == expected_dt

    def test_normalize_different_timezone(self) -> None:
        """Convert datetime from any timezone to target timezone."""
        ny_tz = ZoneInfo('America/New_York')
        dt_ny = datetime(2024, 5, 10, 8, 0, 0, tzinfo=ny_tz)
        normalized = self.normalizer.normalize(dt_ny)

        assert normalized.tzinfo == ZoneInfo('Europe/Berlin')
        expected_dt = dt_ny.astimezone(ZoneInfo('Europe/Berlin'))
        assert normalized == expected_dt

    def test_normalize_preserves_original_datetime(self) -> None:
        """Normalizing a datetime should return a new datetime object, not mutate the original."""
        dt = datetime(2024, 5, 10, 12, 0, 0)  # naive
        dt_before = dt

        normalized = self.normalizer.normalize(dt)

        # Original should remain naive and unchanged
        assert dt == dt_before
        assert dt.tzinfo is None
        assert normalized != dt

    def test_normalize_invalid_input_raises(self) -> None:
        """Passing a non-datetime object to normalize should raise an AttributeError or TypeError."""
        with pytest.raises(AttributeError):
            self.normalizer.normalize('not a datetime')  # type: ignore

        with pytest.raises(AttributeError):
            self.normalizer.normalize(None)  # type: ignore
