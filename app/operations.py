"""Strategy pattern: operation interface and concrete operation strategies."""
from abc import ABC, abstractmethod

from app.exceptions import ValidationError


class Operation(ABC):
    """Abstract base class (Strategy interface) for calculator operations."""

    @abstractmethod
    def execute(self, a: float, b: float) -> float:
        """Perform the operation on two floats and return the result."""
        raise NotImplementedError  # pragma: no cover


class Add(Operation):
    def execute(self, a: float, b: float) -> float:
        return a + b


class Subtract(Operation):
    def execute(self, a: float, b: float) -> float:
        return a - b


class Multiply(Operation):
    def execute(self, a: float, b: float) -> float:
        return a * b


class Divide(Operation):
    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValidationError("Division by zero is not allowed")
        return a / b