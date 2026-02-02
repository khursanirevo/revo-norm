"""
Shared utility functions for currency normalization across languages.

These functions are language-agnostic and can be used by both
English and Malay normalizers.
"""
import re


def expand_currency_k_suffix(m):
    """
    Expand currency with 'K' suffix (thousands) to full number.
    This is entity-aware: only processes detected currency entities.

    This is a universal function that works across all languages.

    Examples:
        RM30K → RM30000
        RM70K → RM70000
        RM1.5K → RM1500
        $50K → $50000
        EUR100K → EUR100000
    """
    symbol = m.group(1)  # RM, $, etc.
    amount = m.group(2)  # e.g., "30", "1.5"

    # Convert to float and multiply by 1000
    amount_float = float(amount) * 1000

    # Convert to integer if it's a whole number
    amount_final = int(amount_float) if amount_float == int(amount_float) else amount_float

    return f"{symbol}{amount_final}"


# Regex pattern for currency with K suffix (thousands)
# Uses (?<!\w) instead of \b to handle symbols like $ that aren't word characters
# This is a universal pattern that works across all languages
CURRENCY_K_SUFFIX_PATTERN = re.compile(
    r'(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)(?:\s?)(\d+(?:\.\d+)?)K\b',
    re.IGNORECASE
)
