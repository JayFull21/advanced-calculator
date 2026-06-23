from __future__ import annotations

from copy import deepcopy
from typing import List


class CalculationMemento:
    """Immutable snapshot of calculator history state."""

    def __init__(self, history: list):
        # deepcopy so later mutations to the originator's history
        # don't leak into the saved snapshot.
        self._state = deepcopy(history)

    def get_state(self) -> list:
        """Return a deep copy of the snapshotted history."""
        return deepcopy(self._state)


class HistoryCaretaker:
    """Holds undo/redo stacks of CalculationMementos."""

    def __init__(self):
        self._undo_stack: List[CalculationMemento] = []
        self._redo_stack: List[CalculationMemento] = []

    def save(self, memento: CalculationMemento) -> None:
        """Push a new snapshot onto the undo stack and clear redo."""
        self._undo_stack.append(memento)
        self._redo_stack.clear()

    def undo(self, current: CalculationMemento) -> CalculationMemento:
        """Pop and return the previous snapshot, pushing current onto redo."""
        if not self._undo_stack:
            raise IndexError("Nothing to undo")
        self._redo_stack.append(current)
        return self._undo_stack.pop()

    def redo(self, current: CalculationMemento) -> CalculationMemento:
        """Pop and return the next snapshot, pushing current onto undo."""
        if not self._redo_stack:
            raise IndexError("Nothing to redo")
        self._undo_stack.append(current)
        return self._redo_stack.pop()

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)