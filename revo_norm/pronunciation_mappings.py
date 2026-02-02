"""
Pronunciation mappings for specific terms.

This module provides explicit pronunciation mappings that should be applied
BEFORE any other transformations (acronym expansion, abbreviation expansion, etc.).

These mappings have the HIGHEST PRIORITY in the normalization pipeline.
"""

from typing import Dict

# English pronunciation mappings
PRONUNCIATION_MAPPINGS_EN: Dict[str, str] = {
    # Technology terms - specific pronunciations
    "JSON": "jay son",
    "GUI": "gooey",
    "SQL": "S Q L",  # Can also be "sequel" depending on preference
    "AJAX": "A JAX",
    "XML": "X M L",
    "HTML": "H T M L",
    "CSS": "C S S",
    "HTTP": "H T T P",
    "HTTPS": "H T T P S",
    "FTP": "F T P",
    "SDK": "S D K",
    "CLI": "C L I",
    "UTF": "U T F",
    "ASCII": "as key",
    "IEEE": "I triple E",
    "UUID": "U U I D",
    "PNG": "ping",
    "JPEG": "J peg",
    "GIF": "gif",
    "SVG": "S V G",
    "PDF": "P D F",
    "URL": "U R L",
    "URI": "U R I",
    "OAuth": "O auth",
    "WiFi": "why fi",
    "iOS": "I O S",
    "VoIP": "V O I P",

    # Tech acronyms - preserve as-is (not split)
    # These are mapped to themselves to prevent acronym splitting
    "API": "API",
    "ML": "ML",
    "AI": "AI",
    "LLM": "LLM",
    "GPU": "GPU",
    "CPU": "CPU",
    "RAM": "RAM",
    "ROM": "ROM",
    "SSD": "SSD",
    "HDD": "HDD",
    "OS": "OS",
    "UI": "UI",
    "UX": "UX",
    "NLP": "NLP",
    "CV": "CV",  # Computer Vision
    "NLU": "NLU",
    "NLG": "NLG",
    "RAG": "RAG",
    "GPT": "GPT",
    "BERT": "BERT",
    "TF": "TF",  # TensorFlow
    "PyTorch": "PyTorch",
    "Keras": "Keras",
    "pandas": "pandas",
    "numpy": "numpy",
}

# Malay pronunciation mappings
PRONUNCIATION_MAPPINGS_MS: Dict[str, str] = {
    # Technology terms (maintain English pronunciation generally)
    "JSON": "jay son",
    "GUI": "gooey",
    "SQL": "S Q L",
    "AJAX": "A JAX",
    "XML": "X M L",
    "HTML": "H T M L",
    "CSS": "C S S",
    "HTTP": "H T T P",
    "HTTPS": "H T T P S",
    "FTP": "F T P",
    "SDK": "S D K",
    "CLI": "C L I",
    "UTF": "U T F",
    "ASCII": "as key",
    "IEEE": "I triple E",
    "UUID": "U U I D",
    "PNG": "ping",
    "JPEG": "J peg",
    "GIF": "gif",
    "SVG": "S V G",
    "PDF": "P D F",
    "URL": "U R L",
    "URI": "U R I",
    "OAuth": "O auth",
    "WiFi": "why fi",
    "iOS": "I O S",
    "VoIP": "V O I P",

    # Tech acronyms - preserve as-is (not split)
    "API": "API",
    "ML": "ML",
    "AI": "AI",
    "LLM": "LLM",
    "GPU": "GPU",
    "CPU": "CPU",
    "RAM": "RAM",
    "ROM": "ROM",
    "SSD": "SSD",
    "HDD": "HDD",
    "OS": "OS",
    "UI": "UI",
    "UX": "UX",
    "NLP": "NLP",
    "CV": "CV",
    "NLU": "NLU",
    "NLG": "NLG",
    "RAG": "RAG",
    "GPT": "GPT",
    "BERT": "BERT",
    "TF": "TF",
    "PyTorch": "PyTorch",
    "Keras": "Keras",
    "pandas": "pandas",
    "numpy": "numpy",
}


def get_pronunciation_mappings(language: str = "en") -> Dict[str, str]:
    """
    Get pronunciation mappings for a language.

    Args:
        language: Language code ('en' for English, 'ms' for Malay)

    Returns:
        Dictionary mapping terms to their spoken forms
    """
    if language == "en":
        return PRONUNCIATION_MAPPINGS_EN.copy()
    elif language == "ms":
        return PRONUNCIATION_MAPPINGS_MS.copy()
    else:
        return {}


def apply_pronunciation_mappings(text: str, language: str = "en") -> str:
    """
    Apply pronunciation mappings to text.

    This should be called FIRST in the normalization pipeline, before any
    other transformations. Mappings are applied as whole-word matches only.

    Terms that are mapped to themselves (e.g., "ML" → "ML") are marked with
    a special prefix to prevent them from being processed by later
    transformations like acronym expansion.

    Args:
        text: Input text
        language: Language code ('en' for English, 'ms' for Malay)

    Returns:
        Text with pronunciation mappings applied

    Example:
        >>> apply_pronunciation_mappings("Parse JSON file", "en")
        'Parse jay son file'
        >>> apply_pronunciation_mappings("JSON API", "en")
        'jay son __PRESERVED__API__'
    """
    import re

    mappings = get_pronunciation_mappings(language)
    if not mappings:
        return text

    # Sort by length (longest first) to handle overlapping matches
    # e.g., "HTTPS" before "HTTP"
    sorted_mappings = sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True)

    result = text
    for term, pronunciation in sorted_mappings:
        # Case-insensitive whole word match
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)

        # If mapping to itself, add preservation marker to prevent acronym expansion
        if term.upper() == pronunciation.upper():
            # Mark as preserved to prevent acronym/abbreviation expansion
            result = pattern.sub(rf"__PRESERVED__{pronunciation}__", result)
        else:
            # Normal pronunciation mapping (e.g., JSON → jay son)
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
        pronunciation: The spoken form (e.g., "jay son")
        language: Language code ('en' or 'ms')
    """
    if language == "en":
        PRONUNCIATION_MAPPINGS_EN[term] = pronunciation
    elif language == "ms":
        PRONUNCIATION_MAPPINGS_MS[term] = pronunciation
