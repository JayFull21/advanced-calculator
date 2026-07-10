import pytest
from pathlib import Path

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove all CALCULATOR_* vars so each test starts from defaults."""
    for var in [
        "CALCULATOR_LOG_DIR", "CALCULATOR_LOG_FILE",
        "CALCULATOR_HISTORY_DIR", "CALCULATOR_HISTORY_FILE",
        "CALCULATOR_MAX_HISTORY_SIZE", "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_PRECISION", "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
    ]:
        monkeypatch.delenv(var, raising=False)


class TestDefaults:
    def test_default_values(self):
        cfg = CalculatorConfig()
        assert cfg.log_dir == Path("logs")
        assert cfg.history_dir == Path("data")
        assert cfg.log_file == Path("logs") / "calculator.log"
        assert cfg.history_file == Path("data") / "history.csv"
        assert cfg.max_history_size == 1000
        assert cfg.auto_save is True
        assert cfg.precision == 10
        assert cfg.max_input_value == 1e12
        assert cfg.default_encoding == "utf-8"


class TestEnvOverrides:
    def test_directories_and_files(self, monkeypatch):
        monkeypatch.setenv("CALCULATOR_LOG_DIR", "mylogs")
        monkeypatch.setenv("CALCULATOR_HISTORY_DIR", "mydata")
        cfg = CalculatorConfig()
        assert cfg.log_dir == Path("mylogs")
        assert cfg.log_file == Path("mylogs") / "calculator.log"
        assert cfg.history_file == Path("mydata") / "history.csv"

    def test_explicit_file_paths_override_dirs(self, monkeypatch):
        monkeypatch.setenv("CALCULATOR_LOG_FILE", "/tmp/x.log")
        monkeypatch.setenv("CALCULATOR_HISTORY_FILE", "/tmp/h.csv")
        cfg = CalculatorConfig()
        assert cfg.log_file == Path("/tmp/x.log")
        assert cfg.history_file == Path("/tmp/h.csv")

    def test_numeric_settings(self, monkeypatch):
        monkeypatch.setenv("CALCULATOR_MAX_HISTORY_SIZE", "50")
        monkeypatch.setenv("CALCULATOR_PRECISION", "2")
        monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "1000")
        cfg = CalculatorConfig()
        assert cfg.max_history_size == 50
        assert cfg.precision == 2
        assert cfg.max_input_value == 1000.0

    @pytest.mark.parametrize("raw, expected", [
        ("true", True), ("false", False), ("1", True),
        ("0", False), ("YES", True), ("no", False),
    ])
    def test_auto_save_parsing(self, monkeypatch, raw, expected):
        monkeypatch.setenv("CALCULATOR_AUTO_SAVE", raw)
        assert CalculatorConfig().auto_save is expected

    def test_encoding(self, monkeypatch):
        monkeypatch.setenv("CALCULATOR_DEFAULT_ENCODING", "latin-1")
        assert CalculatorConfig().default_encoding == "latin-1"


class TestValidation:
    @pytest.mark.parametrize("var, bad", [
        ("CALCULATOR_MAX_HISTORY_SIZE", "abc"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "0"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "-5"),
        ("CALCULATOR_PRECISION", "abc"),
        ("CALCULATOR_PRECISION", "-1"),
        ("CALCULATOR_MAX_INPUT_VALUE", "abc"),
        ("CALCULATOR_MAX_INPUT_VALUE", "0"),
        ("CALCULATOR_MAX_INPUT_VALUE", "-10"),
    ])
    def test_invalid_values_raise(self, monkeypatch, var, bad):
        monkeypatch.setenv(var, bad)
        with pytest.raises(ConfigurationError):
            CalculatorConfig()