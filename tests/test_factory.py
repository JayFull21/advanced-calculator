"""Unit tests for the OperationFactory (Factory pattern)."""
import pytest
from app.exceptions import ValidationError
from app.factory import OperationFactory
from app.operations import Add, Subtract, Multiply, Divide


class TestOperationFactory:
    def test_create_add(self):
        op = OperationFactory.create("add")
        assert isinstance(op, Add)

    def test_create_subtract(self):
        op = OperationFactory.create("subtract")
        assert isinstance(op, Subtract)

    def test_create_multiply(self):
        op = OperationFactory.create("multiply")
        assert isinstance(op, Multiply)

    def test_create_divide(self):
        op = OperationFactory.create("divide")
        assert isinstance(op, Divide)

    def test_create_unsupported_raises(self):
        with pytest.raises(ValidationError, match="Unsupported operation"):
            OperationFactory.create("bogus")

    def test_created_operation_is_usable(self):
        op = OperationFactory.create("add")
        assert op.execute(2, 3) == 5

    def test_valid_operations_returns_all_names(self):
        names = OperationFactory.valid_operations()
        assert names == {
            "add", "subtract", "multiply", "divide",
            "power", "root", "modulus", "int_divide", "percent", "abs_diff",
        }

    def test_factory_integrates_with_validate_operation_name(self):
        from app.input_validators import validate_operation_name

        cleaned = validate_operation_name(
            "  ADD  ", OperationFactory.valid_operations()
        )
        op = OperationFactory.create(cleaned)
        assert isinstance(op, Add)