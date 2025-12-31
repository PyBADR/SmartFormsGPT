"""
Utils package for SmartFormsGPT.

This package contains utility functions and validators.
"""

from utils.helpers import (
    generate_claim_id,
    format_currency,
    parse_date,
    sanitize_text,
    validate_email,
    validate_phone,
    extract_codes,
    calculate_age,
    merge_dicts,
    safe_json_loads
)

from utils.validators import (
    ClaimValidator,
    ValidationError
)

__all__ = [
    # Helpers
    "generate_claim_id",
    "format_currency",
    "parse_date",
    "sanitize_text",
    "validate_email",
    "validate_phone",
    "extract_codes",
    "calculate_age",
    "merge_dicts",
    "safe_json_loads",
    # Validators
    "ClaimValidator",
    "ValidationError"
]
