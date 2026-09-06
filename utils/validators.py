"""Shared input-validation helpers.

Centralizes the "is this number field actually a number" checks so every
form in the project (registration, booking, contact, book payment...)
validates phone numbers the same way instead of each route reinventing
its own half-checked regex.
"""
import re

# Egyptian mobile numbers: 11 digits, starting 010/011/012/015.
PHONE_REGEX = re.compile(r"^01[0125][0-9]{8}$")


def is_valid_phone(value):
    """Return True if `value` looks like a real Egyptian mobile number."""
    if not value:
        return False
    value = value.strip()
    return bool(PHONE_REGEX.match(value))


def clean_phone(value):
    """Strip spaces/dashes people paste in, e.g. '010 123 45678' -> '01012345678'."""
    if not value:
        return ""
    return re.sub(r"[\s\-]", "", value.strip())
