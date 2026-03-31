"""
Pronunciation mappings for specific terms.

This module provides explicit pronunciation mappings that should be applied
BEFORE any other transformations (acronym expansion, abbreviation expansion, etc.).

These mappings have the HIGHEST PRIORITY in the normalization pipeline.

NOTE: JSON, JPEG, PNG and similar acronyms are now handled by a generalized
rule in expand_acronym() - they don't need explicit mappings here.
"""


# Single pronunciation mapping for all languages (English and Malay)
# Tech terms are pronounced the same way in both languages for Malaysian context
PRONUNCIATION_MAPPINGS: dict[str, str] = {
    # Text corrections / OCR error fixes
    "bias": "bai yers",
    # Malay honorifics - pronounced fully for TTS
    "Hj": "Haji",
    "Hjh": "Hajah",
    "Dr": "Doktor",
    "Dr.": "Doktor",
    "Prof": "Profesor",
    "Prof.": "Profesor",
    "Dato": "Dato",
    "Dato'": "Dato",
    "Datin": "Datin",
    "Datuk": "Datuk",
    "AMN": "Ahli Mangku Negara",
    "JSM": "Johan Setia Mahkota",
    "JPM": "Johan Setia Persekutuan",
    "PSM": "Panglima Setia Mahkota",
    "SSM": "Setia Sultan Muhammad",
    "SIM": "Setia Mahkota Pahang",
    "SMP": "Setia Mahkota Perak",
    # Technology terms with special pronunciations (not following generalized rule)
    "GUI": "gooey",
    "ASCII": "as key",
    "IEEE": "I triple E",
    "GIF": "gif",
    "WiFi": "why fi",
    "iOS": "I O S",
}


def get_pronunciation_mappings(language: str = "en") -> dict[str, str]:
    """
    Get pronunciation mappings for a language.

    Args:
        language: Language code ('en' for English, 'ms' for Malay)
                  Note: Same mappings used for both languages

    Returns:
        Dictionary mapping terms to their spoken forms
    """
    # Return a copy to prevent modification of the original
    return PRONUNCIATION_MAPPINGS.copy()


def apply_pronunciation_mappings(text: str, language: str = "en") -> str:
    """
    Apply pronunciation mappings to text.

    This should be called FIRST in the normalization pipeline, before any
    other transformations. Mappings are applied as whole-word matches only.

    NOTE: Only contains actual pronunciation changes (GUI → gooey, etc.).
    All-caps tech acronyms (AI, ML, LLM, GPU, API, etc.) are split
    letter-by-letter by expand_acronym().

    Args:
        text: Input text
        language: Language code ('en' for English, 'ms' for Malay)

    Returns:
        Text with pronunciation mappings applied

    Example:
        >>> apply_pronunciation_mappings("Build GUI interface", "en")
        'Build gooey interface'
        >>> apply_pronunciation_mappings("Train ML model", "en")
        'Train ML model'  # No change here; expand_acronym() will split → "M L"
    """
    import re

    mappings = get_pronunciation_mappings(language)
    if not mappings:
        return text

    # Sort by length (longest first) to handle overlapping matches
    # e.g., "PyTorch" before "torch"
    sorted_mappings = sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)

    result = text
    for term, pronunciation in sorted_mappings:
        # Case-insensitive whole word match
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
        result = pattern.sub(pronunciation, result)

    return result


def remove_preservation_markers(text: str) -> str:
    """
    Remove preservation markers added by pronunciation mappings.

    This should be called at the END of the normalization pipeline to clean up
    the preservation markers.

    Args:
        text: Text with preservation markers

    Returns:
        Clean text without preservation markers

    Example:
        >>> remove_preservation_markers("Train __PRESERVED__ML__ model")
        'Train ML model'
    """
    import re

    return re.sub(r"__PRESERVED__(.+?)__", r"\1", text)


def add_custom_mapping(term: str, pronunciation: str, language: str = "en") -> None:
    """
    Add a custom pronunciation mapping.

    Args:
        term: The term to map (e.g., "JSON")
        pronunciation: The spoken form (e.g., "J son")
        language: Language code ('en' or 'ms') - ignored, applies to both
    """
    PRONUNCIATION_MAPPINGS[term] = pronunciation
