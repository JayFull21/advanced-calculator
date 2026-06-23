import pytest
from app.memento import CalculationMemento, HistoryCaretaker


class TestCalculationMemento:
    def test_stores_state(self):
        memento = CalculationMemento([1, 2, 3])
        assert memento.get_state() == [1, 2, 3]

    def test_state_is_isolated_from_original(self):
        history = [{"op": "add", "result": 5}]
        memento = CalculationMemento(history)
        history.append({"op": "subtract", "result": 1})
        # Memento should still reflect original state, not mutation
        assert memento.get_state() == [{"op": "add", "result": 5}]

    def test_get_state_returns_independent_copy(self):
        memento = CalculationMemento([1, 2, 3])
        snapshot = memento.get_state()
        snapshot.append(99)
        # Subsequent get_state should be unaffected
        assert memento.get_state() == [1, 2, 3]


class TestHistoryCaretaker:
    def test_initially_cannot_undo_or_redo(self):
        c = HistoryCaretaker()
        assert not c.can_undo()
        assert not c.can_redo()

    def test_save_enables_undo(self):
        c = HistoryCaretaker()
        c.save(CalculationMemento([1]))
        assert c.can_undo()
        assert not c.can_redo()

    def test_undo_returns_previous_state(self):
        c = HistoryCaretaker()
        c.save(CalculationMemento([1]))
        current = CalculationMemento([1, 2])
        restored = c.undo(current)
        assert restored.get_state() == [1]
        assert c.can_redo()

    def test_redo_returns_next_state(self):
        c = HistoryCaretaker()
        c.save(CalculationMemento([1]))
        current = CalculationMemento([1, 2])
        previous = c.undo(current)
        # now redo to get back to [1, 2]
        restored = c.redo(previous)
        assert restored.get_state() == [1, 2]

    def test_save_clears_redo_stack(self):
        c = HistoryCaretaker()
        c.save(CalculationMemento([1]))
        c.undo(CalculationMemento([1, 2]))
        assert c.can_redo()
        c.save(CalculationMemento([1, 3]))  # new action
        assert not c.can_redo()

    def test_undo_with_empty_stack_raises(self):
        c = HistoryCaretaker()
        with pytest.raises(IndexError, match="Nothing to undo"):
            c.undo(CalculationMemento([]))

    def test_redo_with_empty_stack_raises(self):
        c = HistoryCaretaker()
        with pytest.raises(IndexError, match="Nothing to redo"):
            c.redo(CalculationMemento([]))