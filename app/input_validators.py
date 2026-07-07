from app.exceptions import ValidationError


def validate_number(value, max_value=None):
    """Validate that a raw input string can be converted to a float.

    If max_value is given, the absolute value must not exceed it.
    Returns the converted float if valid, otherwise raises ValidationError.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid number: {value!r}")
    if max_value is not None and abs(number) > max_value:
        raise ValidationError(
            f"Input {number} exceeds the maximum allowed value of {max_value}"
        )
    return number


def validate_operation_name(name, valid_operations):
    """Validate that the given operation name is supported.

    valid_operations should be an iterable of allowed operation name strings.
    Returns the lowercased, stripped name if valid, otherwise raises ValidationError.
    """
    if not isinstance(name, str):
        raise ValidationError(f"Operation name must be a string, got: {type(name)}")

    cleaned = name.strip().lower()
    if cleaned not in valid_operations:
        raise ValidationError(f"Unsupported operation: {name!r}")

    return cleaned