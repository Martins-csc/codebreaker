"""
CodeBreaker Security & Abuse Guards Module
Provides validation for password strength, input length caps, and security helpers.
"""

import re

LIMITS = {
    "email": 254,
    "password": 128,
    "display_name": 80,
    "project_name": 100,
    "problem": 2000,
    "project_idea": 2000,
    "target_audience": 200,
    "progress": 5000,
    "bugs": 5000,
    "learnings": 5000,
}

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email address format:
    - Non-empty string matching basic email regex (^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$)
    Returns (is_valid, error_message).
    """
    if not email or not isinstance(email, str) or not email.strip():
        return False, "Email cannot be empty."
    if not EMAIL_REGEX.match(email.strip()):
        return False, "Enter a valid email address (e.g. you@school.edu)."
    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength:
    - Minimum 8 characters
    - At least one letter
    - At least one number
    - Maximum 128 characters
    Returns (is_valid, error_message).
    """
    if not password or not isinstance(password, str):
        return (
            False,
            "Password must be at least 8 characters with at least one letter and one number.",
        )
    if len(password) < 8:
        return (
            False,
            "Password must be at least 8 characters with at least one letter and one number.",
        )
    if len(password) > LIMITS["password"]:
        return False, "Input exceeds maximum allowed length. Please shorten your input."

    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return (
            False,
            "Password must be at least 8 characters with at least one letter and one number.",
        )

    return True, ""


def validate_input_length(field_name: str, value: str) -> tuple[bool, str]:
    """
    Validate field value length against defined limits.
    Returns (is_valid, error_message).
    """
    if not value or not isinstance(value, str):
        return True, ""
    limit = LIMITS.get(field_name)
    if limit and len(value) > limit:
        return False, "Input exceeds maximum allowed length. Please shorten your input."
    return True, ""
