from unittest.mock import MagicMock, create_autospec

import pytest

from rebelist.streamline.infrastructure.datetime import DateTimeNormalizer


@pytest.fixture
def mock_datetime_normalizer() -> MagicMock:
    """Mock the container object."""
    mock = create_autospec(spec=DateTimeNormalizer)
    mock.normalize.side_effect = lambda dt: dt

    return mock
