from __future__ import annotations

from app.factory import OperationFactory
from app.memento import CalculationMemento, HistoryCaretaker
from app.observer import Subject
from app.validators import validate_number, validate_operation_name


class Calculator(Subject):
    """Facade over validators, factory, strategies, memento, and observers."""

    def __init__(self):
        super().__init__()
        self._history: list[dict] = []
        self._caretaker = HistoryCaretaker()

    # ----- core API -----

    def calculate(self, operation_name, a, b) -> float:
        """Validate inputs, run the chosen operation, record + notify."""
        name = validate_operation_name(
            operation_name, OperationFactory.valid_operations()
        )
        a_val = validate_number(a)
        b_val = validate_number(b)

        # Snapshot current state BEFORE mutating, so undo restores correctly.
        self._caretaker.save(CalculationMemento(self._history))

        operation = OperationFactory.create(name)
        result = operation.execute(a_val, b_val)

        event = {"operation": name, "a": a_val, "b": b_val, "result": result}
        self._history.append(event)
        self.notify(event)
        return result

    # ----- history access -----

    def get_history(self) -> list[dict]:
        return list(self._history)

    def clear_history(self) -> None:
        self._caretaker.save(CalculationMemento(self._history))
        self._history = []

    # ----- undo / redo -----

    def undo(self) -> None:
        current = CalculationMemento(self._history)
        restored = self._caretaker.undo(current)
        self._history = restored.get_state()

    def redo(self) -> None:
        current = CalculationMemento(self._history)
        restored = self._caretaker.redo(current)
        self._history = restored.get_state()

    def can_undo(self) -> bool:
        return self._caretaker.can_undo()

    def can_redo(self) -> bool:
        return self._caretaker.can_redo()