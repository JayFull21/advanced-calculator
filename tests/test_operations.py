import pytest
from app.exceptions import ValidationError
from app.operations import Add, Subtract, Multiply, Divide, Operation


class TestOperationBase:
    def test_cannot_instantiate_abstract_class(self):
        with pytest.raises(TypeError):
            Operation()


class TestAdd:
    def test_positive_numbers(self):
        assert Add().execute(2, 3) == 5

    def test_negative_numbers(self):
        assert Add().execute(-2, -3) == -5

    def test_mixed_sign(self):
        assert Add().execute(-2, 5) == 3

    def test_floats(self):
        assert Add().execute(1.5, 2.5) == 4.0


class TestSubtract:
    def test_positive_result(self):
        assert Subtract().execute(5, 3) == 2

    def test_negative_result(self):
        assert Subtract().execute(3, 5) == -2

    def test_floats(self):
        assert Subtract().execute(5.5, 2.0) == 3.5


class TestMultiply:
    def test_positive_numbers(self):
        assert Multiply().execute(4, 3) == 12

    def test_with_zero(self):
        assert Multiply().execute(4, 0) == 0

    def test_negative_numbers(self):
        assert Multiply().execute(-2, 3) == -6

    def test_floats(self):
        assert Multiply().execute(2.5, 4) == 10.0


class TestDivide:
    def test_positive_numbers(self):
        assert Divide().execute(10, 2) == 5

    def test_negative_numbers(self):
        assert Divide().execute(-10, 2) == -5

    def test_floats(self):
        assert Divide().execute(7.5, 2.5) == 3.0

    def test_division_by_zero_raises(self):
        with pytest.raises(ValidationError, match="Division by zero"):
            Divide().execute(5, 0)