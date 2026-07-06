"""Factory pattern: builds Operation instances from operation name strings."""
from app.exceptions import ValidationError
from app.operations import (
    Add,
    Subtract,
    Multiply,
    Divide,
    Power,
    Root,
    Modulus,
    IntDivide,
    Percent,
    AbsDiff,
    Operation,
)


class OperationFactory:
    """Factory for creating Operation strategy instances by name."""

    _operations = {
        "add": Add,
        "subtract": Subtract,
        "multiply": Multiply,
        "divide": Divide,
        "power": Power,
        "root": Root,
        "modulus": Modulus,
        "int_divide": IntDivide,
        "percent": Percent,
        "abs_diff": AbsDiff,
    }

    @classmethod
    def create(cls, name: str) -> Operation:
        """Return a new Operation instance matching the given name.

        Expects `name` to already be validated/normalized (lowercased,
        stripped) e.g. via validate_operation_name.
        """
        operation_cls = cls._operations.get(name)
        if operation_cls is None:
            raise ValidationError(f"Unsupported operation: {name!r}")
        return operation_cls()

    @classmethod
    def valid_operations(cls):
        """Return the set of supported operation names."""
        return set(cls._operations.keys())