"""Unit tests for the CalculatorREPL."""
import pytest
from app.calculator import Calculator
from app.history import HistoryManager
from app.repl import CalculatorREPL


@pytest.fixture
def repl(tmp_path):
    calc = Calculator(HistoryManager(csv_path=tmp_path / "h.csv"))
    return CalculatorREPL(calc)


def run_lines(repl, lines):
    """Helper: feed lines into repl.run via fake input, capture output."""
    outputs = []
    inputs = iter(lines + ["exit"])
    repl.run(input_fn=lambda _: next(inputs), output_fn=outputs.append)
    return outputs


class TestCommands:
    def test_calculation(self, repl):
        outs = run_lines(repl, ["add 2 3"])
        assert any("= 5" in o for o in outs)

    def test_help(self, repl):
        outs = run_lines(repl, ["help"])
        assert any("Commands:" in o for o in outs)

    def test_history_empty(self, repl):
        outs = run_lines(repl, ["history"])
        assert any("(empty)" in o for o in outs)

    def test_history_with_entries(self, repl):
        outs = run_lines(repl, ["add 1 2", "history"])
        # Should contain something resembling the calculation row
        assert any("add" in o for o in outs)

    def test_clear(self, repl):
        outs = run_lines(repl, ["add 1 2", "clear"])
        assert any("cleared" in o.lower() for o in outs)

    def test_undo_with_nothing(self, repl):
        outs = run_lines(repl, ["undo"])
        assert any("Nothing to undo" in o for o in outs)

    def test_undo_after_calc(self, repl):
        outs = run_lines(repl, ["add 1 2", "undo"])
        assert any("Undone" in o for o in outs)

    def test_redo_with_nothing(self, repl):
        outs = run_lines(repl, ["redo"])
        assert any("Nothing to redo" in o for o in outs)

    def test_redo_after_undo(self, repl):
        outs = run_lines(repl, ["add 1 2", "undo", "redo"])
        assert any("Redone" in o for o in outs)

    def test_unknown_command(self, repl):
        outs = run_lines(repl, ["frobnicate"])
        assert any("Unknown command" in o for o in outs)

    def test_invalid_operation_shows_error(self, repl):
        outs = run_lines(repl, ["power 2 3"])
        assert any("Error" in o for o in outs)

    def test_invalid_number_shows_error(self, repl):
        outs = run_lines(repl, ["add abc 3"])
        assert any("Error" in o for o in outs)

    def test_empty_line_is_skipped(self, repl):
        outs = run_lines(repl, ["", "add 1 1"])
        assert any("= 2" in o for o in outs)


class TestPersistenceCommands:
    def test_save_and_load(self, tmp_path):
        path = tmp_path / "hist.csv"
        calc = Calculator(HistoryManager(csv_path=path))
        repl = CalculatorREPL(calc)
        outs = run_lines(repl, ["add 1 2", "save"])
        assert any("Saved to" in o for o in outs)
        assert path.exists()

        # New REPL, load it
        calc2 = Calculator(HistoryManager(csv_path=path))
        repl2 = CalculatorREPL(calc2)
        outs2 = run_lines(repl2, ["load", "history"])
        assert any("loaded" in o.lower() for o in outs2)

    def test_load_missing_file(self, tmp_path):
        path = tmp_path / "nope.csv"
        calc = Calculator(HistoryManager(csv_path=path))
        repl = CalculatorREPL(calc)
        outs = run_lines(repl, ["load"])
        assert any("not found" in o.lower() for o in outs)


class TestExit:
    def test_exit_command(self, repl):
        outs = run_lines(repl, [])  # just "exit" from helper
        assert any("Goodbye" in o for o in outs)

    def test_quit_command(self, repl):
        outputs = []
        inputs = iter(["quit"])
        repl.run(input_fn=lambda _: next(inputs), output_fn=outputs.append)
        assert any("Goodbye" in o for o in outputs)

    def test_eof_exits_cleanly(self, repl):
        def raise_eof(_):
            raise EOFError
        repl.run(input_fn=raise_eof, output_fn=lambda _: None)