"""Observer pattern: Subject base + concrete Observers for calculation events."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List


class Observer(ABC):
    """Abstract Observer interface."""

    @abstractmethod
    def update(self, event: dict) -> None:
        """React to an event published by a Subject."""
        raise NotImplementedError  # pragma: no cover


class Subject:
    """Mixin/base providing observer attach/detach/notify behavior."""

    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: dict) -> None:
        for observer in list(self._observers):
            observer.update(event)


class LoggingObserver(Observer):
    """Logs each calculation event using the standard logging module."""

    def __init__(self, logger: logging.Logger | None = None):
        self._logger = logger or logging.getLogger("calculator")

    def update(self, event: dict) -> None:
        self._logger.info(
            "Calculation: %s(%s, %s) = %s",
            event.get("operation"),
            event.get("a"),
            event.get("b"),
            event.get("result"),
        )


class HistoryObserver(Observer):
    """Collects calculation events into an in-memory list."""

    def __init__(self):
        self.records: list[dict] = []

    def update(self, event: dict) -> None:
        self.records.append(event)