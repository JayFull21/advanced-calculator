"""Unit tests for color-coded output helpers (colorama optional feature)."""
from colorama import Fore, Style

from app.colors import error, info, success, warning


class TestColorHelpers:
    def test_success_is_green(self):
        out = success("done")
        assert out.startswith(Fore.GREEN)
        assert "done" in out
        assert out.endswith(Style.RESET_ALL)

    def test_error_is_red(self):
        out = error("boom")
        assert out.startswith(Fore.RED)
        assert "boom" in out

    def test_info_is_cyan(self):
        out = info("hello")
        assert out.startswith(Fore.CYAN)
        assert "hello" in out

    def test_warning_is_yellow(self):
        out = warning("careful")
        assert out.startswith(Fore.YELLOW)
        assert "careful" in out

    def test_original_text_always_preserved(self):
        for fn in (success, error, info, warning):
            assert "payload" in fn("payload")


class TestReplColorIntegration:
    def test_result_output_is_green(self, tmp_path):
        from app.calculator import Calculator
        from app.history import HistoryManager
        from app.repl import CalculatorREPL

        repl = CalculatorREPL(Calculator(HistoryManager(csv_path=tmp_path / "h.csv")))
        outs = []
        repl.handle("add 2 3", outs.append)
        assert any(Fore.GREEN in o and "= 5" in o for o in outs)

    def test_error_output_is_red(self, tmp_path):
        from app.calculator import Calculator
        from app.history import HistoryManager
        from app.repl import CalculatorREPL

        repl = CalculatorREPL(Calculator(HistoryManager(csv_path=tmp_path / "h.csv")))
        outs = []
        repl.handle("divide 1 0", outs.append)
        assert any(Fore.RED in o and "Error" in o for o in outs)