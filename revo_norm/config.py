"""
Normalization configuration system for revo-norm.

This module provides a more intuitive API for configuring text normalization
using profiles and feature groups instead of individual boolean flags.

Example:
    >>> from revo_norm.config import NormalizationConfig, Profile, FeatureGroup, FeatureLevel
    >>> config = NormalizationConfig.from_preset("standard")
    >>> config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
    >>> from revo_norm import normalize_text
    >>> result = normalize_text("The API uses 5GB", language="en", config=config)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Union


class Profile(str, Enum):
    """Normalization presets for different TTS use cases."""

    MINIMAL = "minimal"
    """Basic cleanup only. Good for: Plain text that's already well-formatted."""

    BASIC = "basic"
    """Standard normalization. Good for: General text, conversations, emails."""

    STANDARD = "standard"
    """Full normalization. Good for: News, articles, formal text (DEFAULT)."""

    AGGRESSIVE = "aggressive"
    """Maximum normalization. Good for: Social media, informal text, OCR output."""


class FeatureGroup(str, Enum):
    """Logical groupings of related normalization features."""

    # Core features (always active in some form)
    NUMBERS = "numbers"
    """Number-to-words, currency, dates, times, fractions."""

    ENTITIES = "entities"
    """URLs, emails, phone numbers, letter-period sequences."""

    SPACING = "spacing"
    """Whitespace normalization, punctuation cleanup."""

    # Content-specific features
    MEASUREMENTS = "measurements"
    """Temperature, distance, weight, volume, duration units."""

    MALAY_LOCAL = "malay_local"
    """Malay-specific: hari bulan, hijri, IC numbers, x-kali (MS only)."""

    ABBREVIATIONS = "abbreviations"
    """Expand short forms (km → kilometer, sqrt → square root)."""

    ACRONYMS = "acronyms"
    """Expand acronyms letter-by-letter (API → A P I)."""

    # Text quality features
    ELONGATED = "elongated"
    """Fix elongated words (verrry → verry)."""

    # Date/time entities (NEW)
    DATES = "dates"
    """Date recognition and normalization (15/08/2025 → spoken form)."""

    TIMES = "times"
    """Time recognition and normalization (3:30 pm → spoken form)."""


class FeatureLevel(str, Enum):
    """Intensity levels for feature groups."""

    OFF = "off"
    """Don't process this feature group."""

    BASIC = "basic"
    """Minimal processing."""

    STANDARD = "standard"
    """Full processing (default for most features)."""

    AGGRESSIVE = "aggressive"
    """Maximum processing."""


# Profile definitions: feature_group -> level for each profile
_PROFILE_DEFINITIONS: Dict[Profile, Dict[FeatureGroup, FeatureLevel]] = {
    Profile.MINIMAL: {
        FeatureGroup.NUMBERS: FeatureLevel.BASIC,
        FeatureGroup.ENTITIES: FeatureLevel.STANDARD,
        FeatureGroup.SPACING: FeatureLevel.STANDARD,
        FeatureGroup.MEASUREMENTS: FeatureLevel.OFF,
        FeatureGroup.MALAY_LOCAL: FeatureLevel.OFF,
        FeatureGroup.ABBREVIATIONS: FeatureLevel.OFF,
        FeatureGroup.ACRONYMS: FeatureLevel.OFF,
        FeatureGroup.ELONGATED: FeatureLevel.OFF,
        FeatureGroup.DATES: FeatureLevel.OFF,
        FeatureGroup.TIMES: FeatureLevel.OFF,
    },
    Profile.BASIC: {
        FeatureGroup.NUMBERS: FeatureLevel.STANDARD,
        FeatureGroup.ENTITIES: FeatureLevel.STANDARD,
        FeatureGroup.SPACING: FeatureLevel.STANDARD,
        FeatureGroup.MEASUREMENTS: FeatureLevel.BASIC,
        FeatureGroup.MALAY_LOCAL: FeatureLevel.OFF,
        FeatureGroup.ABBREVIATIONS: FeatureLevel.BASIC,
        FeatureGroup.ACRONYMS: FeatureLevel.OFF,
        FeatureGroup.ELONGATED: FeatureLevel.OFF,
        FeatureGroup.DATES: FeatureLevel.STANDARD,  # Dates are basic need
        FeatureGroup.TIMES: FeatureLevel.STANDARD,  # Times are basic need
    },
    Profile.STANDARD: {
        FeatureGroup.NUMBERS: FeatureLevel.STANDARD,
        FeatureGroup.ENTITIES: FeatureLevel.STANDARD,
        FeatureGroup.SPACING: FeatureLevel.STANDARD,
        FeatureGroup.MEASUREMENTS: FeatureLevel.STANDARD,
        FeatureGroup.MALAY_LOCAL: FeatureLevel.BASIC,  # Only active for MS
        FeatureGroup.ABBREVIATIONS: FeatureLevel.STANDARD,
        FeatureGroup.ACRONYMS: FeatureLevel.STANDARD,
        FeatureGroup.ELONGATED: FeatureLevel.OFF,
        FeatureGroup.DATES: FeatureLevel.STANDARD,
        FeatureGroup.TIMES: FeatureLevel.STANDARD,
    },
    Profile.AGGRESSIVE: {
        FeatureGroup.NUMBERS: FeatureLevel.AGGRESSIVE,
        FeatureGroup.ENTITIES: FeatureLevel.STANDARD,
        FeatureGroup.SPACING: FeatureLevel.STANDARD,
        FeatureGroup.MEASUREMENTS: FeatureLevel.AGGRESSIVE,
        FeatureGroup.MALAY_LOCAL: FeatureLevel.STANDARD,  # Only active for MS
        FeatureGroup.ABBREVIATIONS: FeatureLevel.STANDARD,
        FeatureGroup.ACRONYMS: FeatureLevel.AGGRESSIVE,
        FeatureGroup.ELONGATED: FeatureLevel.STANDARD,
        FeatureGroup.DATES: FeatureLevel.STANDARD,
        FeatureGroup.TIMES: FeatureLevel.STANDARD,
    },
}


@dataclass
class NormalizationConfig:
    """
    Configuration for text normalization.

    Attributes:
        profile: Preset profile to use (default: standard)
        language: Language code ('en' or 'ms')
        features: Feature group overrides (applied on top of profile)
        sound_words: Sound words to remove (e.g., "[laughter]", "[applause]")
        custom_rules: Custom pronunciation rules (future feature)

    Example:
        >>> config = NormalizationConfig(profile=Profile.STANDARD)
        >>> config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
        >>> config.get_level(FeatureGroup.ACRONYMS)
        'off'
    """

    profile: Union[Profile, str] = Profile.STANDARD
    language: Optional[str] = None
    features: Dict[FeatureGroup, FeatureLevel] = field(default_factory=dict)
    sound_words: List[str] = field(default_factory=list)
    custom_rules: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration after initialization."""
        if isinstance(self.profile, str):
            self.profile = Profile(self.profile)

    @classmethod
    def from_preset(cls, profile: Union[Profile, str], **kwargs) -> "NormalizationConfig":
        """
        Create config from preset profile with optional overrides.

        Args:
            profile: Profile name or enum
            **kwargs: Additional config options

        Returns:
            NormalizationConfig instance

        Example:
            >>> config = NormalizationConfig.from_preset("aggressive", language="ms")
        """
        return cls(profile=profile, **kwargs)

    def with_feature(self, group: Union[FeatureGroup, str], level: Union[FeatureLevel, str]):
        """
        Set a feature group level (builder pattern).

        Args:
            group: Feature group to set
            level: Level to set for the group

        Returns:
            self (for chaining)

        Example:
            >>> config = NormalizationConfig.from_preset("standard")
            >>> config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
        """
        if isinstance(group, str):
            group = FeatureGroup(group)
        if isinstance(level, str):
            level = FeatureLevel(level)
        self.features[group] = level
        return self

    def with_sound_words(self, words: List[str]):
        """
        Set sound words to remove (builder pattern).

        Args:
            words: List of sound word patterns

        Returns:
            self (for chaining)
        """
        self.sound_words = words
        return self

    def get_level(self, group: FeatureGroup) -> FeatureLevel:
        """
        Get the effective level for a feature group.

        Checks overrides first, then falls back to profile definition.

        Args:
            group: Feature group to query

        Returns:
            FeatureLevel for the group
        """
        # Check for explicit override
        if group in self.features:
            return self.features[group]

        # Fall back to profile definition
        return _PROFILE_DEFINITIONS[Profile(self.profile)][group]

    def is_enabled(self, group: FeatureGroup) -> bool:
        """
        Check if a feature group is enabled (level != OFF).

        Args:
            group: Feature group to check

        Returns:
            True if the feature is enabled
        """
        return self.get_level(group) != FeatureLevel.OFF

    def should_run_feature(self, group: FeatureGroup, language: str) -> bool:
        """
        Check if a feature should run for a specific language.

        Some features (like MALAY_LOCAL) only run for Malay.

        Args:
            group: Feature group to check
            language: Language code ('en' or 'ms')

        Returns:
            True if the feature should run for this language
        """
        level = self.get_level(group)

        if level == FeatureLevel.OFF:
            return False

        # Malay-specific features only run for Malay
        if group == FeatureGroup.MALAY_LOCAL and language != "ms":
            return False

        return True

    def to_legacy_flags(self, language: str) -> dict:
        """
        Convert config to legacy boolean flags for backward compatibility.

        This allows the new config system to work with the existing normalize_text()
        function that uses individual boolean flags.

        Args:
            language: Language code ('en' or 'ms')

        Returns:
            Dictionary of legacy flag names to boolean values
        """
        return {
            "normalize_spacing": (self.get_level(FeatureGroup.SPACING) != FeatureLevel.OFF),
            "fix_dot_letters": (self.get_level(FeatureGroup.ENTITIES) != FeatureLevel.OFF),
            "apply_pronunciation_overrides_flag": (
                self.get_level(FeatureGroup.NUMBERS) != FeatureLevel.OFF
            ),
            "expand_abbreviations_flag": (
                self.get_level(FeatureGroup.ABBREVIATIONS) != FeatureLevel.OFF
            ),
            "expand_acronyms_flag": (self.get_level(FeatureGroup.ACRONYMS) != FeatureLevel.OFF),
            "normalize_elongated_flag": (
                self.get_level(FeatureGroup.ELONGATED) != FeatureLevel.OFF
            ),
            "normalize_fractions_flag": (self.get_level(FeatureGroup.NUMBERS) != FeatureLevel.OFF),
            "normalize_x_kali_flag": (self.should_run_feature(FeatureGroup.MALAY_LOCAL, language)),
            "normalize_temperature_flag": (
                self.get_level(FeatureGroup.MEASUREMENTS) != FeatureLevel.OFF
            ),
            "normalize_ic_flag": (self.should_run_feature(FeatureGroup.MALAY_LOCAL, language)),
            "normalize_measurements_flag": (
                self.get_level(FeatureGroup.MEASUREMENTS) != FeatureLevel.OFF
            ),
            "normalize_hari_bulan_flag": (
                self.should_run_feature(FeatureGroup.MALAY_LOCAL, language)
            ),
            "normalize_hijri_flag": (self.should_run_feature(FeatureGroup.MALAY_LOCAL, language)),
            "sound_words_field": "\n".join(self.sound_words),
        }

    def __repr__(self) -> str:
        """String representation of config."""
        features_repr = ", ".join(f"{k}={v}" for k, v in self.features.items())
        return f"NormalizationConfig(profile={self.profile}, features={{{features_repr}}})"


# Convenience functions for common configs


def minimal_config(**kwargs) -> NormalizationConfig:
    """Create a minimal normalization config."""
    return NormalizationConfig.from_preset(Profile.MINIMAL, **kwargs)


def basic_config(**kwargs) -> NormalizationConfig:
    """Create a basic normalization config."""
    return NormalizationConfig.from_preset(Profile.BASIC, **kwargs)


def standard_config(**kwargs) -> NormalizationConfig:
    """Create a standard normalization config."""
    return NormalizationConfig.from_preset(Profile.STANDARD, **kwargs)


def aggressive_config(**kwargs) -> NormalizationConfig:
    """Create an aggressive normalization config."""
    return NormalizationConfig.from_preset(Profile.AGGRESSIVE, **kwargs)


# Preset configurations for common use cases


def conversation_config(language: str = "en") -> NormalizationConfig:
    """
    Config for casual conversation/text messages.

    Enables measurements and elongated word fixing.
    """
    config = NormalizationConfig.from_preset(Profile.BASIC, language=language)
    config.with_feature(FeatureGroup.MEASUREMENTS, FeatureLevel.STANDARD)
    if language == "ms":
        config.with_feature(FeatureGroup.ELONGATED, FeatureLevel.STANDARD)
    return config


def news_config(language: str = "en") -> NormalizationConfig:
    """
    Config for news articles and formal text.

    Standard normalization without aggressive changes.
    """
    return NormalizationConfig.from_preset(Profile.STANDARD, language=language)


def social_media_config(language: str = "en") -> NormalizationConfig:
    """
    Config for social media text.

    Aggressive normalization including elongated words and slang.
    """
    config = NormalizationConfig.from_preset(Profile.AGGRESSIVE, language=language)
    return config


def technical_doc_config(language: str = "en") -> NormalizationConfig:
    """
    Config for technical documentation.

    Preserves acronyms (API, CPU) but expands abbreviations.
    """
    config = NormalizationConfig.from_preset(Profile.STANDARD, language=language)
    config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
    return config
