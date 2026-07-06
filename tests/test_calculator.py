import pytest
from app.calculator import Calculator
from app.exceptions import ValidationError
from app.history import HistoryManager
from app.observer import HistoryObserver


@pytest.fixture
def calc(tmp_path):
    """Calculator with an isolated HistoryManager (no real CSV path used)."""
    return Calculator(HistoryManager(csv_path=tmp_path / "h.csv"))


class TestBasicCalculations:
    def test_add(self, calc):
        assert calc.calculate("add", 2, 3) == 5

    def test_subtract(self, calc):
        assert calc.calculate("subtract", 10, 4) == 6

    def test_multiply(self, calc):
        assert calc.calculate("multiply", 3, 4) == 12

    def test_divide(self, calc):
        assert calc.calculate("divide", 10, 2) == 5

    def test_accepts_string_numbers(self, calc):
        assert calc.calculate("add", "1.5", "2.5") == 4.0

    def test_normalizes_operation_name(self, calc):
        assert calc.calculate("  ADD ", 1, 1) == 2


class TestValidationErrors:
    def test_invalid_operation_raises(self, calc):
        with pytest.raises(ValidationError):
            calc.calculate("bogus", 2, 3)

    def test_invalid_number_raises(self, calc):
        with pytest.raises(ValidationError):
            calc.calculate("add", "abc", 3)

    def test_divide_by_zero_raises(self, calc):
        with pytest.raises(ValidationError):
            calc.calculate("divide", 5, 0)


class TestHistory:
    def test_history_records_calculations(self, calc):
        calc.calculate("add", 1, 2)
        calc.calculate("multiply", 3, 4)
        df = calc.get_history()
        assert len(df) == 2
        assert df.iloc[0]["operation"] == "add"
        assert df.iloc[1]["result"] == 12

    def test_get_history_returns_copy(self, calc):
        calc.calculate("add", 1, 2)
        df = calc.get_history()
        df.drop(df.index, inplace=True)
        assert len(calc.get_history()) == 1

    def test_clear_history(self, calc):
        calc.calculate("add", 1, 2)
        calc.clear_history()
        assert len(calc.get_history()) == 0


class TestUndoRedo:
    def test_undo_reverts_last_calculation(self, calc):
        calc.calculate("add", 1, 2)
        calc.calculate("add", 3, 4)
        calc.undo()
        df = calc.get_history()
        assert len(df) == 1
        assert df.iloc[0]["result"] == 3

    def test_redo_reapplies_undone_calculation(self, calc):
        calc.calculate("add", 1, 2)
        calc.calculate("add", 3, 4)
        calc.undo()
        calc.redo()
        assert len(calc.get_history()) == 2

    def test_undo_then_new_calc_clears_redo(self, calc):
        calc.calculate("add", 1, 2)
        calc.calculate("add", 3, 4)
        calc.undo()
        calc.calculate("multiply", 2, 2)
        assert not calc.can_redo()

    def test_can_undo_initially_false(self, calc):
        assert not calc.can_undo()

    def test_can_undo_true_after_calc(self, calc):
        calc.calculate("add", 1, 1)
        assert calc.can_undo()

    def test_undo_with_no_history_raises(self, calc):
        with pytest.raises(IndexError):
            calc.undo()

    def test_redo_with_nothing_to_redo_raises(self, calc):
        with pytest.raises(IndexError):
            calc.redo()

    def test_clear_history_is_undoable(self, calc):
        calc.calculate("add", 1, 2)
        calc.clear_history()
        calc.undo()
        assert len(calc.get_history()) == 1


class TestPersistence:
    def test_save_and_load_history(self, tmp_path):
        path = tmp_path / "saved.csv"
        c1 = Calculator(HistoryManager(csv_path=path))
        c1.calculate("add", 1, 2)
        c1.calculate("multiply", 3, 4)
        c1.save_history()

        c2 = Calculator(HistoryManager(csv_path=path))
        c2.load_history()
        df = c2.get_history()
        assert len(df) == 2
        assert df.iloc[1]["result"] == 12


class TestObserverIntegration:
    def test_observer_notified_on_calculation(self, calc):
        hist = HistoryObserver()
        calc.attach(hist)
        calc.calculate("add", 2, 3)
        assert len(hist.records) == 1
        assert hist.records[0]["result"] == 5

    def test_detached_observer_not_notified(self, calc):
        hist = HistoryObserver()
        calc.attach(hist)
        calc.detach(hist)
        calc.calculate("add", 2, 3)
        assert hist.records == []