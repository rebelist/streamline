from pytest_mock import MockerFixture

from rebelist.streamline.infrastructure.monitoring import Logger


def test_logger_info_calls_loguru_info(mocker: MockerFixture) -> None:
    """Test that Logger.info() correctly delegates to loguru's info() method."""
    mock_loguru_logger = mocker.MagicMock()
    logger = Logger(mock_loguru_logger)

    logger.info('Test message')

    mock_loguru_logger.opt.assert_called_once_with(depth=1)
    mock_loguru_logger.opt.return_value.remove.assert_called_once()
    mock_loguru_logger.opt.return_value.add.assert_called_once()
    mock_loguru_logger.opt.return_value.info.assert_called_once_with('Test message')


def test_logger_warning_calls_loguru_warning(mocker: MockerFixture) -> None:
    """Test that Logger.warning() correctly delegates to loguru's warning() method."""
    mock_loguru_logger = mocker.MagicMock()
    logger = Logger(mock_loguru_logger)

    logger.warning('Warning message')

    mock_loguru_logger.opt.return_value.warning.assert_called_once_with('Warning message')


def test_logger_error_calls_loguru_error(mocker: MockerFixture) -> None:
    """Test that Logger.error() correctly delegates to loguru's error() method."""
    mock_loguru_logger = mocker.MagicMock()
    logger = Logger(mock_loguru_logger)

    logger.error('Error message')

    mock_loguru_logger.opt.return_value.error.assert_called_once_with('Error message')
