"""Configuration management: loads and validates CALCULATOR_* env settings."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError


TRUTHY = {"1", "true", "yes", "on"}


class CalculatorConfig:
    """Loads CALCULATOR_* environment variables with validated defaults.

    Priority for every setting: environment variable (via .env or the
    shell) if set, otherwise a sensible default.
    """

    def __init__(self):
        load_dotenv()

        # --- base directories ---
        self.log_dir = Path(os.getenv("CALCULATOR_LOG_DIR", "logs"))
        self.history_dir = Path(os.getenv("CALCULATOR_HISTORY_DIR", "data"))

        # --- file paths (explicit file env vars override dir-based defaults) ---
        log_file = os.getenv("CALCULATOR_LOG_FILE")
        self.log_file = Path(log_file) if log_file else self.log_dir / "calculator.log"

        history_file = os.getenv("CALCULATOR_HISTORY_FILE")
        self.history_file = (
            Path(history_file) if history_file else self.history_dir / "history.csv"
        )

        # --- history settings ---
        self.max_history_size = self._positive_int(
            "CALCULATOR_MAX_HISTORY_SIZE", default=1000
        )
        self.auto_save = (
            os.getenv("CALCULATOR_AUTO_SAVE", "true").strip().lower() in TRUTHY
        )

        # --- calculation settings ---
        self.precision = self._non_negative_int("CALCULATOR_PRECISION", default=10)
        self.max_input_value = self._positive_float(
            "CALCULATOR_MAX_INPUT_VALUE", default=1e12
        )
        self.default_encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    # ----- validated parsers -----

    @staticmethod
    def _positive_int(name: str, default: int) -> int:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            value = int(raw)
        except ValueError:
            raise ConfigurationError(f"{name} must be an integer, got: {raw!r}")
        if value <= 0:
            raise ConfigurationError(f"{name} must be positive, got: {value}")
        return value

    @staticmethod
    def _non_negative_int(name: str, default: int) -> int:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            value = int(raw)
        except ValueError:
            raise ConfigurationError(f"{name} must be an integer, got: {raw!r}")
        if value < 0:
            raise ConfigurationError(f"{name} must not be negative, got: {value}")
        return value

    @staticmethod
    def _positive_float(name: str, default: float) -> float:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            value = float(raw)
        except ValueError:
            raise ConfigurationError(f"{name} must be a number, got: {raw!r}")
        if value <= 0:
            raise ConfigurationError(f"{name} must be positive, got: {value}")
        return value