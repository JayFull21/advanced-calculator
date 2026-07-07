"""Logging setup: routes calculator logs to the configured log file."""
from __future__ import annotations

import logging

from app.calculator_config import CalculatorConfig


LOGGER_NAME = "calculator"


def configure_logging(config: CalculatorConfig | None = None) -> logging.Logger:
    """Attach a FileHandler for the configured log file to the calculator logger.

    Creates the log directory if it doesn't exist. Safe to call multiple
    times: a handler for the same file is only added once.
    """
    config = config or CalculatorConfig()
    config.log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    target = str(config.log_file.resolve())
    already_attached = any(
        isinstance(h, logging.FileHandler)
        and getattr(h, "baseFilename", None) == target
        for h in logger.handlers
    )
    if not already_attached:
        handler = logging.FileHandler(
            config.log_file, encoding=config.default_encoding
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logger.addHandler(handler)

    return logger