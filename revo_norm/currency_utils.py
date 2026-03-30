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


def expand_currency_m_suffix(m):
    """
    Expand currency with 'M' suffix (millions) to word form.
    Outputs "{symbol}{amount} million" so the downstream currency regex
    can handle it without the raw large number confusing other normalizers.

    Examples:
        RM19m  → RM19 million
        $5M    → $5 million
        RM1.5M → RM1.5 million
    """
    symbol = m.group(1)
    amount = m.group(2)
    return f"{symbol}{amount} million"


def expand_currency_b_suffix(m):
    """
    Expand currency with 'B' suffix (billions) to word form.

    Examples:
        RM1B   → RM1 billion
        $2.5B  → $2.5 billion
    """
    symbol = m.group(1)
    amount = m.group(2)
    return f"{symbol}{amount} billion"


def expand_currency_t_suffix(m):
    """
    Expand currency with 'T' suffix (trillions) to word form.

    Examples:
        RM1T → RM1 trillion
        $2T  → $2 trillion
    """
    symbol = m.group(1)
    amount = m.group(2)
    return f"{symbol}{amount} trillion"


# Regex pattern for currency with K suffix (thousands)
# Uses (?<!\w) instead of \b to handle symbols like $ that aren't word characters
# This is a universal pattern that works across all languages
CURRENCY_K_SUFFIX_PATTERN = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)(?:\s?)(\d+(?:\.\d+)?)K\b", re.IGNORECASE
)

# Regex pattern for currency with M suffix (millions)
CURRENCY_M_SUFFIX_PATTERN = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)(?:\s?)(\d+(?:\.\d+)?)M\b", re.IGNORECASE
)

# Regex pattern for currency with B suffix (billions)
CURRENCY_B_SUFFIX_PATTERN = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)(?:\s?)(\d+(?:\.\d+)?)B\b", re.IGNORECASE
)

# Regex pattern for currency with T suffix (trillions)
CURRENCY_T_SUFFIX_PATTERN = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)(?:\s?)(\d+(?:\.\d+)?)T\b", re.IGNORECASE
)
