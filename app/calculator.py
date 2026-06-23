from __future__ import annotations

from app.factory import OperationFactory
from app.history import HistoryManager
from app.memento import CalculationMemento, HistoryCaretaker
from app.observer import Subject
from app.validators import validate_number, validate_operation_name


class Calculator(Subject):
    """Facade over validators, factory, strategies, memento, observers, history."""

    def __init__(self, history_manager: HistoryManager | None = None):
        super().__init__()
        self._history = history_manager or HistoryManager()
        self._caretaker = HistoryCaretaker()

    # ----- core API -----

    def calculate(self, operation_name, a, b) -> float:
        name = validate_operation_name(
            operation_name, OperationFactory.valid_operations()
        )
        a_val = validate_number(a)
        b_val = validate_number(b)

        # Snapshot pre-mutation state for undo.
        self._caretaker.save(CalculationMemento(self._history.dataframe))

        operation = OperationFactory.create(name)
        result = operation.execute(a_val, b_val)

        event = {"operation": name, "a": a_val, "b": b_val, "result": result}
        self._history.add(event)
        self.notify(event)
        return result

    # ----- history access -----

    def get_history(self):
        """Return history as a pandas DataFrame (copy)."""
        return self._history.dataframe

    def clear_history(self) -> None:
        self._caretaker.save(CalculationMemento(self._history.dataframe))
        self._history.clear()

    def save_history(self, path=None):
        return self._history.save(path)

    def load_history(self, path=None) -> None:
        self._history.load(path)

    # ----- undo / redo -----

    def undo(self) -> None:
        current = CalculationMemento(self._history.dataframe)
        restored = self._caretaker.undo(current)
        self._restore(restored.get_state())

    def redo(self) -> None:
        current = CalculationMemento(self._history.dataframe)
        restored = self._caretaker.redo(current)
        self._restore(restored.get_state())

    def _restore(self, df) -> None:
        self._history.clear()
        for _, row in df.iterrows():
            self._history.add(row.to_dict())

    def can_undo(self) -> bool:
        return self._caretaker.can_undo()

    def can_redo(self) -> bool:
        return self._caretaker.can_redo()