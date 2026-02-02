"""
Revo Norm - A text normalization library for English and Malay TTS applications.

This library provides text normalization capabilities for Text-to-Speech (TTS) applications,
specifically designed for English and Malay (Bahasa Melayu) languages.

Example usage:
    >>> from revo_norm import normalize_text
    >>> result = normalize_text("Hello, this is a test.", language="en")
    >>> print(result)
"""

__version__ = "0.1.0"

# Main API exports
from revo_norm.text_normalizer import (
    normalize_text,
    normalize_whitespace,
    email_to_spoken,
    expand_capitalized_initialisms,
    split_into_sentences,
)

# English normalizer
from revo_norm.normalizer_en import text_normalize as normalize_english

# Malay normalizer
from revo_norm.normalizer_ms import normalize_malay as normalize_malay

# Number to words (Malay)
from revo_norm.num2word import to_cardinal, to_ordinal, to_currency, to_year

# Abbreviation utilities
from revo_norm.abbreviation_utils import (
    expand_abbreviations,
    get_abbreviation_mapping,
    add_custom_abbreviation,
)

# Malaya-inspired utilities
from revo_norm.malaya_inspired_utils import (
    normalize_elongated_text,
    normalize_fractions,
    normalize_x_kali_text,
    normalize_temperatures,
    normalize_ic_numbers,
    normalize_measurements,
    normalize_hari_bulan_text,
    normalize_hijri_years,
)

__all__ = [
    # Version
    "__version__",
    # Main API
    "normalize_text",
    "normalize_whitespace",
    "email_to_spoken",
    "expand_capitalized_initialisms",
    "split_into_sentences",
    # Language-specific normalizers
    "normalize_english",
    "normalize_malay",
    # Number-to-words (Malay)
    "to_cardinal",
    "to_ordinal",
    "to_currency",
    "to_year",
    # Abbreviation utilities
    "expand_abbreviations",
    "get_abbreviation_mapping",
    "add_custom_abbreviation",
    # Malaya-inspired utilities
    "normalize_elongated_text",
    "normalize_fractions",
    "normalize_x_kali_text",
    "normalize_temperatures",
    "normalize_ic_numbers",
    "normalize_measurements",
    "normalize_hari_bulan_text",
    "normalize_hijri_years",
]
