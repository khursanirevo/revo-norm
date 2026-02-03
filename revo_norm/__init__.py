"""
Revo Norm - A text normalization library for English and Malay TTS applications.

This library provides text normalization capabilities for Text-to-Speech (TTS) applications,
specifically designed for English and Malay (Bahasa Melayu) languages.

Example usage:
    >>> from revo_norm import normalize_text
    >>> result = normalize_text("Hello, this is a test.", language="en")
    >>> print(result)

New API (recommended):
    >>> from revo_norm import normalize_text, standard_config
    >>> result = normalize_text("25C outside", language="en", config=standard_config())
"""

__version__ = "0.2.0-dev"

# Main API exports
# Abbreviation utilities
from revo_norm.abbreviation_utils import (
    add_custom_abbreviation,
    expand_abbreviations,
    get_abbreviation_mapping,
)

# New configuration system (recommended)
from revo_norm.config import (
    FeatureGroup,
    FeatureLevel,
    NormalizationConfig,
    Profile,
    aggressive_config,
    basic_config,
    conversation_config,
    minimal_config,
    news_config,
    social_media_config,
    standard_config,
    technical_doc_config,
)

# Entity extraction system (experimental)
from revo_norm.entity_extractor import Entity, EntityExtractor, EntityType

# Malaya-inspired utilities
from revo_norm.malaya_inspired_utils import (
    normalize_elongated_text,
    normalize_fractions,
    normalize_hari_bulan_text,
    normalize_hijri_years,
    normalize_ic_numbers,
    normalize_measurements,
    normalize_temperatures,
    normalize_x_kali_text,
)

# English normalizer
from revo_norm.normalizer_en import text_normalize as normalize_english

# Malay normalizer
from revo_norm.normalizer_ms import normalize_malay as normalize_malay

# Number to words (Malay)
from revo_norm.num2word import to_cardinal, to_currency, to_ordinal, to_year

# TTS-specific utilities
from revo_norm.tts_utils import (
    add_random_commas,
    normalize_problematic_chars,
    parse_sound_word_field,
    smart_remove_sound_words,
    split_repetitive_sequences,
    split_text_by_words,
)

# Main text normalizer
from revo_norm.text_normalizer import (
    email_to_spoken,
    expand_capitalized_initialisms,
    normalize_text,
    normalize_whitespace,
    split_into_sentences,
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
    # New configuration system (recommended)
    "NormalizationConfig",
    "Profile",
    "FeatureGroup",
    "FeatureLevel",
    "minimal_config",
    "basic_config",
    "standard_config",
    "aggressive_config",
    "conversation_config",
    "news_config",
    "social_media_config",
    "technical_doc_config",
    # Entity extraction system (experimental)
    "Entity",
    "EntityExtractor",
    "EntityType",
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
    # TTS-specific utilities
    "normalize_problematic_chars",
    "parse_sound_word_field",
    "smart_remove_sound_words",
    "split_repetitive_sequences",
    "split_text_by_words",
    "add_random_commas",
]
