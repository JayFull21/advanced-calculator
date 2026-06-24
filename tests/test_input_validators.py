"""Unit tests for validate_number and validate_operation_name."""
import pytest
from app.exceptions import ValidationError
from app.input_validators import validate_number, validate_operation_name


class TestValidateNumber:
    def test_valid_integer_string(self):
        assert validate_number("42") == 42.0

    def test_valid_float_string(self):
        assert validate_number("3.14") == 3.14

    def test_negative_number_string(self):
        assert validate_number("-7.5") == -7.5

    def test_valid_float_type_passthrough(self):
        assert validate_number(2.5) == 2.5

    def test_valid_int_type_passthrough(self):
        assert validate_number(10) == 10.0

    def test_invalid_string_raises(self):
        with pytest.raises(ValidationError):
            validate_number("abc")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_number(None)

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            validate_number("")

    def test_error_message_contains_value(self):
        with pytest.raises(ValidationError, match="not_a_number"):
            validate_number("not_a_number")


class TestValidateOperationName:
    VALID_OPS = {"add", "subtract", "multiply", "divide"}

    def test_valid_lowercase_name(self):
        assert validate_operation_name("add", self.VALID_OPS) == "add"

    def test_strips_whitespace(self):
        assert validate_operation_name("  add  ", self.VALID_OPS) == "add"

    def test_lowercases_input(self):
        assert validate_operation_name("ADD", self.VALID_OPS) == "add"

    def test_mixed_case_with_whitespace(self):
        assert validate_operation_name(" SuBtRaCt ", self.VALID_OPS) == "subtract"

    def test_unsupported_operation_raises(self):
        with pytest.raises(ValidationError):
            validate_operation_name("power", self.VALID_OPS)

    def test_non_string_input_raises(self):
        with pytest.raises(ValidationError):
            validate_operation_name(123, self.VALID_OPS)

    def test_none_input_raises(self):
        with pytest.raises(ValidationError):
            validate_operation_name(None, self.VALID_OPS)

    def test_error_message_for_unsupported_op(self):
        with pytest.raises(ValidationError, match="power"):
            validate_operation_name("power", self.VALID_OPS)

    def test_error_message_for_non_string(self):
        with pytest.raises(ValidationError, match="must be a string"):
            validate_operation_name(3.14, self.VALID_OPS)