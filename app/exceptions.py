"""Custom exception hierarchy for the calculator application."""


class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass


class ValidationError(CalculatorError):
    """Raised when user input fails validation (e.g. non-numeric input)."""
    pass


class InvalidOperationError(CalculatorError):
    """Raised when an unsupported or unrecognized operation is requested."""
    pass


class DivisionByZeroError(CalculatorError):
    """Raised when a division (or root/power edge case) by zero is attempted."""
    pass

class ConfigurationError(CalculatorError):
    """Raised when an environment configuration value is invalid."""
    pass


class DataLoadError(CalculatorError):
    """Raised when a history CSV file is malformed or unreadable."""
    pass