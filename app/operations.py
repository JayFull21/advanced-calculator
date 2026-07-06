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


class Power(Operation):
    """Raise a to the power of b."""

    def execute(self, a: float, b: float) -> float:
        if a == 0 and b < 0:
            raise ValidationError("Zero cannot be raised to a negative power")
        if a < 0 and b != int(b):
            raise ValidationError(
                "Negative base with a fractional exponent is not supported"
            )
        return a ** b


class Root(Operation):
    """Calculate the b-th root of a."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValidationError("Root degree cannot be zero")
        if a < 0:
            if b != int(b) or int(b) % 2 == 0:
                raise ValidationError(
                    "Cannot take an even or fractional root of a negative number"
                )
            # Odd integer root of a negative number is negative.
            return -((-a) ** (1 / b))
        return a ** (1 / b)


class Modulus(Operation):
    """Compute the remainder of a divided by b."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValidationError("Modulus by zero is not allowed")
        return a % b


class IntDivide(Operation):
    """Perform integer (floor) division of a by b, discarding the fraction."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValidationError("Integer division by zero is not allowed")
        return a // b


class Percent(Operation):
    """Calculate a as a percentage of b: (a / b) * 100."""

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValidationError("Cannot compute a percentage of zero")
        return (a / b) * 100


class AbsDiff(Operation):
    """Calculate the absolute difference between a and b."""

    def execute(self, a: float, b: float) -> float:
        return abs(a - b)