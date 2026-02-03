"""
Abbreviation and short form expansion utilities for text normalization.

NOTE: Abbreviation expansion has been DISABLED due to context-sensitivity issues.
Common words like "in" cannot be reliably distinguished from measurement units without
complex context analysis that introduces false positives.

For TTS applications, rely on:
- Number normalization (handles measurements with spoken forms)
- Acronym expansion (capitalized initialisms)
- Pronunciation mappings (explicit spoken forms)
"""


def expand_abbreviations(text: str, language: str = "en") -> str:
    """
    No-op placeholder for backward compatibility.

    Abbreviation expansion disabled due to context-sensitivity issues.
    Returns text unchanged.
    """
    return text


def get_abbreviation_mapping(language: str = "en") -> dict:
    """Returns empty dict for backward compatibility."""
    return {}


def add_custom_abbreviation(abbr: str, full_form: str, language: str = "en") -> None:
    """No-op placeholder for backward compatibility."""
    pass
