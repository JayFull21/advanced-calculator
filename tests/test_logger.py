"""Unit tests for configure_logging (file logging setup)."""
import logging

import pytest

from app.calculator_config import CalculatorConfig
from app.logger import configure_logging, LOGGER_NAME


@pytest.fixture
def clean_logger():
    """Detach any file handlers before and after each test."""
    logger = logging.getLogger(LOGGER_NAME)

    def strip():
        for h in list(logger.handlers):
            if isinstance(h, logging.FileHandler):
                logger.removeHandler(h)
                h.close()

    strip()
    yield logger
    strip()


@pytest.fixture
def config(tmp_path, monkeypatch):
    monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path / "logs" / "calc.log"))
    return CalculatorConfig()


class TestConfigureLogging:
    def test_creates_log_directory(self, clean_logger, config):
        configure_logging(config)
        assert config.log_file.parent.exists()

    def test_writes_messages_to_file(self, clean_logger, config):
        logger = configure_logging(config)
        logger.info("Calculation: add(2, 3) = 5")
        for h in logger.handlers:
            h.flush()
        contents = config.log_file.read_text()
        assert "add(2, 3) = 5" in contents
        assert "[INFO]" in contents

    def test_idempotent_no_duplicate_handlers(self, clean_logger, config):
        configure_logging(config)
        logger = configure_logging(config)
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert len(file_handlers) == 1

    def test_default_config_when_none_given(self, clean_logger, tmp_path, monkeypatch):
        monkeypatch.setenv("CALCULATOR_LOG_FILE", str(tmp_path / "default.log"))
        logger = configure_logging()
        logger.info("hello")
        for h in logger.handlers:
            h.flush()
        assert (tmp_path / "default.log").exists()

    def test_observer_events_reach_log_file(self, clean_logger, config, tmp_path):
        from app.calculator import Calculator
        from app.history import HistoryManager
        from app.observer import LoggingObserver

        logger = configure_logging(config)
        calc = Calculator(HistoryManager(csv_path=tmp_path / "h.csv"))
        calc.attach(LoggingObserver())
        calc.calculate("multiply", 6, 7)
        for h in logger.handlers:
            h.flush()
        assert "multiply" in config.log_file.read_text()