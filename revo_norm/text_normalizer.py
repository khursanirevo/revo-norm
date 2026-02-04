import re
from typing import TYPE_CHECKING, List, Optional, Tuple

from revo_norm.abbreviation_utils import expand_abbreviations
from revo_norm.currency_utils import (
    CURRENCY_K_SUFFIX_PATTERN,
    CURRENCY_M_SUFFIX_PATTERN,
    CURRENCY_B_SUFFIX_PATTERN,
    CURRENCY_T_SUFFIX_PATTERN,
    expand_currency_k_suffix,
    expand_currency_m_suffix,
    expand_currency_b_suffix,
    expand_currency_t_suffix,
)
from revo_norm.pronunciation_mappings import apply_pronunciation_mappings, remove_preservation_markers
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
from revo_norm.normalizer_en import text_normalize as text_normalizer_en
from revo_norm.normalizer_ms import normalize_malay as text_normalizer_ms

# Type check import to avoid circular dependency
if TYPE_CHECKING:
    from revo_norm.config import NormalizationConfig


def normalize_whitespace(text: str) -> str:
    """Normalize multiple whitespace to single space and strip."""
    return re.sub(r"\s{2,}", " ", text.strip())


def email_to_spoken(email: str, language: str = "en") -> str:
    """
    Convert an email address into a spoken-friendly form for TTS.

    Args:
        email: Email address to convert
        language: Target language ('en' or 'ms'). Defaults to 'en'.

    Returns:
        Spoken form of the email address

    Example:
        >>> email_to_spoken("sugumaran_thiagarajan@yahoo.com", "en")
        'sugumaran underscore thiagarajan at yahoo dot com'
        >>> email_to_spoken("sugumaran_thiagarajan@yahoo.com", "ms")
        'sugumaran underscore thiagarajan at yahoo dot com'
    """
    # Use "at" for @ symbol in both English and Malay
    at_word = "at"
    spoken = email.replace("@", f" {at_word} ")
    # Replace all dots with " dot " (not just .com)
    spoken = spoken.replace(".", " dot ")
    spoken = spoken.replace("_", " underscore ")
    spoken = spoken.replace("+", " plus ")
    # Replace hyphen with " dash " in emails
    spoken = spoken.replace("-", " dash ")

    return re.sub(r"\s+", " ", spoken).strip()


# Email regex pattern
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE)


def convert_emails_to_spoken(text: str, language: str = "en") -> str:
    """
    Find all email addresses in text and convert them to spoken form using regex.
    This prevents messing up dots in other parts of the text.

    Args:
        text: Input text containing email addresses
        language: Target language ('en' or 'ms'). Defaults to 'en'.

    Returns:
        Text with email addresses converted to spoken form
    """

    def replace_email(match):
        email = match.group(0)
        return email_to_spoken(email, language)

    return _EMAIL_RE.sub(replace_email, text)


def url_to_spoken(url: str) -> str:
    """
    Convert a URL/website into a spoken-friendly form for TTS.

    Examples:
        'www.google.com' -> 'w w w dot google dot com'
        'http://192.168.1.1:8080/path' -> 'h t t p colon slash slash one nine two...'
    """
    spoken = url

    # Replace protocol FIRST - generalize by splitting on ://
    if "://" in spoken:
        protocol, rest = spoken.split("://", 1)
        # Spell out protocol character by character
        protocol_spoken = " ".join(list(protocol))
        spoken = spoken.replace(f"{protocol}://", f"{protocol_spoken} colon slash slash ")

    # Replace www
    spoken = re.sub(r"www\.?", "w w w dot ", spoken)

    # Handle port numbers separately (before general processing)
    def replace_port(match):
        port = match.group(1)
        port_digits = " ".join(list(port))
        return f" colon {port_digits}"

    spoken = re.sub(r":(\d+)", replace_port, spoken)

    # Replace remaining dots with " dot "
    spoken = spoken.replace(".", " dot ")

    # Replace slashes with " slash "
    spoken = spoken.replace("/", " slash ")

    # Replace remaining numbers with digit-by-digit speaking (for IP addresses)
    def speak_number_digits(match):
        num = match.group(0)
        return " ".join(list(num))

    spoken = re.sub(r"\d+", speak_number_digits, spoken)

    # Replace hyphens with " dash "
    spoken = spoken.replace("-", " dash ")

    # Clean up extra spaces
    spoken = re.sub(r"\s+", " ", spoken).strip()

    return spoken


# URL regex pattern - matches any protocol://, www., IPs, domains, and ports
# Entity-specific: Requires protocol/www OR stricter domain pattern to avoid
# matching currency (e.g., RM1.5K)
_URL_RE = re.compile(
    r"(?:[a-zA-Z][a-zA-Z0-9+.-]*://|www\.)[^\s]+|"  # Any protocol:// URLs (must start with protocol/www)
    r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?|"  # IP addresses
    r"\b[A-Za-z0-9-]+\.[A-Za-z]{2,}(?:/[^\s]*)?",  # Simple domains (e.g., example.com)
    re.IGNORECASE,
)


def convert_urls_to_spoken(text: str) -> str:
    """
    Find all URLs/websites in text and convert them to spoken form using regex.
    This prevents messing up dots and slashes in other parts of the text.
    """

    def replace_url(match):
        url = match.group(0)
        return url_to_spoken(url)

    return _URL_RE.sub(replace_url, text)


def replace_letter_period_sequences(text: str, process_acronyms: bool = True) -> str:
    """
    Replace letter period sequences like 'I.B.M.' with 'I B M'.

    This handles all variations of capitalized abbreviations:
    - I.B.M. → I B M
    - IBM → I B M
    - I.B.M → I B M
    - I. B. M. → I B M (already spaces)

    Args:
        text: Input text
        process_acronyms: If True, also handle all-caps acronyms (IBM, API, CPU).
                        If False, only handle letter-period sequences.

    Note: This is now the ONLY place that handles acronym/initialism expansion.
    Abbreviations that were letter-by-letter (API, CPU, etc.) have been removed
    from the abbreviation list to avoid double-processing.
    """

    # First, handle letter-period sequences (I.B.M., A.B.C., etc.)
    def replacer_periods(match):
        cleaned = match.group(0).rstrip(".")
        letters = cleaned.split(".")
        return " ".join(letters)

    text = re.sub(r"\b(?:[A-Za-z]\.){2,}\.?", replacer_periods, text)

    # Then, handle remaining all-caps sequences (IBM, API, CPU, etc.) - ONLY if requested
    if process_acronyms:
        # But only if they're 2-4 letters (avoid matching regular words)
        def replacer_caps(match):
            acronym = match.group(0)
            # Use the existing expand_acronym logic
            return expand_acronym(acronym)

        # Match 2-4 consecutive uppercase letters that form a word
        # This catches things like IBM, API, CPU that weren't caught by letter-period pattern
        text = re.sub(r"\b[A-Z]{2,4}\b", replacer_caps, text)

    return text


# Keep the original expand_capitalized_initialisms as an alias for compatibility
expand_capitalized_initialisms = replace_letter_period_sequences


def remove_inline_reference_numbers(text: str) -> str:
    """Remove reference numbers after punctuation (e.g., 'word1.' -> 'word.')."""
    pattern = r'([.!?,\\\'"\)\]])(\d+)(?=\s|$)'
    return re.sub(pattern, r"\1", text)


def is_pronounceable(acronym: str) -> bool:
    """Check if an acronym is pronounceable based on vowel count."""
    vowels = set("AEIOUaeiou")
    return sum(ch in vowels for ch in acronym) >= 2


KNOWN_LETTERWISE = {"UOB", "UIA", "UITM", "KLIA", "KLIA2"}


def expand_acronym(acronym: str) -> str:
    """Expand an acronym into spoken form."""
    if acronym in KNOWN_LETTERWISE:
        return " ".join(list(acronym))
    if is_pronounceable(acronym) and len(acronym) > 3:
        return acronym
    return " ".join(list(acronym))


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic regex."""
    sentence_endings = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
    return [s.strip() for s in sentence_endings.split(text) if s.strip()]


def parse_sound_word_field(user_input: str) -> List[Tuple[str, str]]:
    """Parse sound word field input into list of (pattern, replacement) tuples."""
    lines = [line.strip() for line in user_input.split("\n") if line.strip()]
    result = []
    for line in lines:
        if "=>" in line:
            pattern, replacement = line.split("=>", 1)
            result.append((pattern.strip(), replacement.strip()))
        else:
            result.append((line, ""))
    return result


def smart_remove_sound_words(text: str, sound_words: List[Tuple[str, str]]) -> str:
    """Remove or replace sound words like [laughter], [applause] from text."""
    for pattern, replacement in sound_words:
        if replacement:
            text = re.sub(
                r"(?i)(%s)([" r"'\u2019`s?])" % re.escape(pattern),
                lambda m: replacement + "'s" if m.group(2) else replacement,
                text,
            )
            if all(char in "-—-" for char in pattern.strip()):
                text = re.sub(re.escape(pattern), replacement, text)
            else:
                text = re.sub(
                    r"\b%s\b" % re.escape(pattern), replacement, text, flags=re.IGNORECASE
                )
        else:
            text = re.sub(r"%s" % re.escape(pattern), "", text, flags=re.IGNORECASE)

    # Use pre-compiled patterns
    text = _CAMEL_CASE_PATTERN.sub(r"\1 \2", text)
    text = _MULTIPLE_COMMAS_PATTERN.sub(",", text)
    text = _COMMAS_WITH_SPACES_PATTERN.sub(",", text)
    text = _MULTI_SPACE_PATTERN.sub(" ", text)
    text = _SPACE_COMMA_SPACE_PATTERN.sub(", ", text)
    text = _LEADING_COMMA_PATTERN.sub(r"\1", text)
    text = _TRAILING_COMMA_PATTERN.sub(r"\1", text)
    return text.strip()


# Pre-compiled regex patterns for smart_remove_sound_words
_CAMEL_CASE_PATTERN = re.compile(r"([a-z])([A-Z])")
_MULTIPLE_COMMAS_PATTERN = re.compile(r"([,\s]+,)+")
_COMMAS_WITH_SPACES_PATTERN = re.compile(r",\s*,+")
_MULTI_SPACE_PATTERN = re.compile(r"\s{2,}")
_SPACE_COMMA_SPACE_PATTERN = re.compile(r"(\s+,|,\s+)")
_LEADING_COMMA_PATTERN = re.compile(r"(^|[\.!\?]\s*),+")
_TRAILING_COMMA_PATTERN = re.compile(r",+\s*([\.!\?])")


def insert_comma_after_repeated_words(text: str, min_repeat: int = 3) -> str:
    """Insert comma after repeated words (e.g., 'test test test test' -> 'test test test, test')."""
    pattern = re.compile(r"\b(?P<word>\w+)\b(?: \1){" + str(min_repeat) + r",}", re.IGNORECASE)

    def replacer(match):
        phrase = match.group(0)
        words = phrase.split()
        return " ".join(words[:-1]) + ", " + words[-1]

    return pattern.sub(replacer, text)


# Pre-compiled regex patterns for pronunciation overrides (performance optimization)
_PRONUNCIATION_OVERRIDE_PATTERNS = [
    (re.compile(r"\btwenty-three\b", re.IGNORECASE), "twenty tree"),
    (re.compile(r"\bthree\b", re.IGNORECASE), "three"),
    (re.compile(r"\btwenty-eight\b", re.IGNORECASE), "twenty, eight"),
    (re.compile(r"\bcut-off\b", re.IGNORECASE), "kad off"),
    (re.compile(r"\beighty-eight\b", re.IGNORECASE), "eighty eight"),
    (re.compile(r"\bNumber\b", re.IGNORECASE), "number"),
    (re.compile(r"\ba/l\b", re.IGNORECASE), "anak lelaki"),
    (re.compile(r"\ba/p\b", re.IGNORECASE), "anak perempuan"),
    (re.compile(r"\b1Malaysia\b", re.IGNORECASE), "satu malaysia"),
    (re.compile(r"\bNo\.\b", re.IGNORECASE), "number"),
]

# Pre-compiled unit patterns for pronunciation overrides
_PRONUNCIATION_UNIT_MAP = {
    "mg": (re.compile(r"(\d+)\s*mg\b", re.IGNORECASE), "milligram"),
    "kg": (re.compile(r"(\d+)\s*kg\b", re.IGNORECASE), "kilogram"),
    "GB": (re.compile(r"(\d+)\s*GB\b", re.IGNORECASE), "gigabyte"),
    # Note: "hb" (hari bulan) is handled by normalize_hari_bulan_text
}


def apply_pronunciation_overrides(text: str) -> str:
    """Apply pronunciation overrides for specific words and phrases."""
    # Apply precompiled patterns
    for pattern, replacement in _PRONUNCIATION_OVERRIDE_PATTERNS:
        text = pattern.sub(replacement, text)

    # Apply unit patterns
    for unit, (pattern, spoken) in _PRONUNCIATION_UNIT_MAP.items():
        text = pattern.sub(rf"\1 {spoken}", text)

    return text


def special_replace(text: str, language: str = "en") -> str:
    """
    Special character and punctuation normalization.
    This function replaces special characters with spoken equivalents.
    """
    # Language-specific replacements
    percent_word = "percent" if language == "en" else "peratus"

    replacements = {
        "&": "and",
        "+": "plus",
        "=": "equals",
        "@": "at",
        "#": "hash",
        "*": "star",
        "%": percent_word,
        "$": "dollar",
        "EUR": "euro",
        "GBP": "pound",
        "©": "copyright",
        "®": "registered",
        "™": "trademark",
        "<": "less than",
        ">": "greater than",
        "|": "bar",
        "~": "tilde",
        "^": "caret",
    }

    for char, replacement in replacements.items():
        text = text.replace(char, f" {replacement} ")

    # Clean up multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(
    text: str,
    language: str = "en",
    config: Optional["NormalizationConfig"] = None,
    # New entity extraction flag
    extract_entities_first: bool = False,
    # Legacy flags (deprecated but still supported for backward compatibility)
    normalize_spacing: bool = True,
    fix_dot_letters: bool = True,
    sound_words_field: str = "",
    apply_pronunciation_overrides_flag: bool = True,
    expand_abbreviations_flag: bool = True,
    expand_acronyms_flag: bool = True,
    normalize_elongated_flag: bool = True,
    normalize_fractions_flag: bool = True,
    normalize_x_kali_flag: bool = True,
    normalize_temperature_flag: bool = True,
    normalize_ic_flag: bool = True,
    normalize_measurements_flag: bool = True,
    normalize_hari_bulan_flag: bool = True,
    normalize_hijri_flag: bool = True,
) -> str:
    """
    Main text normalization function.

    Args:
        text: The input text to normalize
        language: Language code ('en' for English, 'ms' for Malay)
        config: NormalizationConfig object (NEW - recommended approach).
                If provided, legacy flags are ignored.
        extract_entities_first: If True, use entity extraction approach.
                              Extracts entities first, processes non-entity text safely,
                              then restores entities as spoken form. Prevents pattern
                              conflicts (e.g., date vs fraction). EXPERIMENTAL.
        expand_acronyms_flag: Whether to expand acronyms letter-by-letter (NEW)
        [legacy flags]: Individual boolean flags (DEPRECATED - use config instead).
                        These are still supported for backward compatibility.

    Returns:
        Normalized text string

    Examples:
        >>> # New API (recommended)
        >>> from revo_norm.config import standard_config
        >>> result = normalize_text("Hello world", language="en", config=standard_config())

        >>> # Simple usage (uses standard profile)
        >>> result = normalize_text("Hello world", language="en")

        >>> # With custom config
        >>> from revo_norm.config import NormalizationConfig, FeatureGroup, FeatureLevel
        >>> config = NormalizationConfig.from_preset("standard")
        >>> config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
        >>> result = normalize_text("The API is fast", language="en", config=config)

        >>> # Legacy API (still works)
        >>> result = normalize_text("Hello", language="en", normalize_spacing=True)
    """
    text = text.strip()
    if not text or len(text) == 0:
        return ""

    # NEW: Entity extraction approach
    # Check if extract_entities_first flag is set, regardless of config
    if extract_entities_first:
        return _normalize_with_entity_extraction(text, language, config)

    # Handle new config system vs legacy flags
    if config is not None:
        # Use new config-based approach

        # Override language if specified in config
        effective_language = config.language or language

        # Convert config to legacy flags for backward compatibility
        # This allows us to keep the existing implementation while supporting new API
        legacy_flags = config.to_legacy_flags(effective_language)

        normalize_spacing = legacy_flags["normalize_spacing"]
        fix_dot_letters = legacy_flags["fix_dot_letters"]
        sound_words_field = legacy_flags["sound_words_field"]
        apply_pronunciation_overrides_flag = legacy_flags["apply_pronunciation_overrides_flag"]
        expand_abbreviations_flag = legacy_flags["expand_abbreviations_flag"]
        expand_acronyms_flag = legacy_flags["expand_acronyms_flag"]
        normalize_elongated_flag = legacy_flags["normalize_elongated_flag"]
        normalize_fractions_flag = legacy_flags["normalize_fractions_flag"]
        normalize_x_kali_flag = legacy_flags["normalize_x_kali_flag"]
        normalize_temperature_flag = legacy_flags["normalize_temperature_flag"]
        normalize_ic_flag = legacy_flags["normalize_ic_flag"]
        normalize_measurements_flag = legacy_flags["normalize_measurements_flag"]
        normalize_hari_bulan_flag = legacy_flags["normalize_hari_bulan_flag"]
        normalize_hijri_flag = legacy_flags["normalize_hijri_flag"]
    else:
        # Use legacy flags (backward compatibility)
        effective_language = language

    # Expand currency suffixes FIRST (before URL/email conversion)
    # Order matters: T → B → M → K (largest to smallest)
    # This ensures RM1T/RM1B/RM1M/RM30K become full numbers before URL processing breaks them
    text = CURRENCY_T_SUFFIX_PATTERN.sub(lambda m: expand_currency_t_suffix(m), text)
    text = CURRENCY_B_SUFFIX_PATTERN.sub(lambda m: expand_currency_b_suffix(m), text)
    text = CURRENCY_M_SUFFIX_PATTERN.sub(lambda m: expand_currency_m_suffix(m), text)
    text = CURRENCY_K_SUFFIX_PATTERN.sub(lambda m: expand_currency_k_suffix(m), text)

    # Convert emails and URLs (after K expansion to avoid breaking currency patterns)
    # NOTE: Process emails BEFORE URLs to prevent URL pattern from matching
    # the domain part of email addresses (e.g., example.com in user@example.com)
    text = convert_emails_to_spoken(text, effective_language)
    text = convert_urls_to_spoken(text)

    # Apply pronunciation mappings FIRST (highest priority)
    # This must happen before acronym/abbreviation expansion to prevent
    # terms like "JSON" from being split into "J S O N"
    text = apply_pronunciation_mappings(text, effective_language)

    # Apply pronunciation overrides (legacy, for backward compatibility)
    if apply_pronunciation_overrides_flag:
        text = apply_pronunciation_overrides(text)

    # Malaya-inspired normalizations (before language-specific processing)
    if normalize_elongated_flag:
        text = normalize_elongated_text(text)
    if normalize_fractions_flag:
        text = normalize_fractions(text, effective_language)
    if normalize_x_kali_flag:
        text = normalize_x_kali_text(text, effective_language)
    if normalize_temperature_flag:
        text = normalize_temperatures(text, effective_language)
    if normalize_ic_flag:
        text = normalize_ic_numbers(text, effective_language)
    if normalize_measurements_flag:
        text = normalize_measurements(text, effective_language)
    # Hari bulan normalization BEFORE language-specific (using underscore to avoid contraction)
    if normalize_hari_bulan_flag:
        text = normalize_hari_bulan_text(text, effective_language)
    if normalize_hijri_flag:
        text = normalize_hijri_years(text, effective_language)

    # Language-specific normalization
    if effective_language == "en":
        text = text_normalizer_en(text)
    elif effective_language == "ms":
        text = text_normalizer_ms(text)

    # Remove sound words
    if sound_words_field and sound_words_field.strip():
        sound_words = parse_sound_word_field(sound_words_field)
        if sound_words:
            text = smart_remove_sound_words(text, sound_words)

    # Expand abbreviations and short forms (e.g., km -> kilometer, sqrt -> square root)
    if expand_abbreviations_flag:
        text = expand_abbreviations(text, effective_language)

    # Normalize spacing
    if normalize_spacing:
        text = normalize_whitespace(text)

    # Handle letter-period sequences and optionally acronyms
    # Letter-period: I.B.M. → I B M (always runs if fix_dot_letters is enabled)
    # Acronyms: IBM → I B M (only runs if expand_acronyms_flag is enabled)
    if fix_dot_letters or expand_acronyms_flag:
        text = replace_letter_period_sequences(text, process_acronyms=expand_acronyms_flag)

    # Insert comma after repeated words
    text = insert_comma_after_repeated_words(text, min_repeat=3)

    # Apply special character replacements
    text = special_replace(text, effective_language)

    # Remove preservation markers from pronunciation mappings
    # This must be done LAST to prevent acronym/abbreviation expansion
    # from interfering with preserved terms
    text = remove_preservation_markers(text)

    return text


def _normalize_with_entity_extraction(
    text: str,
    language: str,
    config: Optional["NormalizationConfig"],
) -> str:
    """
    Normalize text using entity extraction approach.

    This 3-phase approach prevents pattern conflicts:
    1. Extract entities → replace with placeholders
    2. Process non-entity text safely (NO basic normalization to avoid placeholder processing)
    3. Restore entities as spoken form

    Args:
        text: Input text
        language: Language code
        config: Normalization config

    Returns:
        Normalized text
    """
    from revo_norm.entity_extractor import EntityExtractor, EntityType

    try:
        # Determine effective language
        effective_language = language
        if config and config.language:
            effective_language = config.language

        # Determine which entities to extract based on config
        # Always extract these (they have specific patterns that don't conflict)
        # IMPORTANT: Extract EMAIL before URL to prevent URL pattern from matching domain in emails
        always_extract = [
            EntityType.EMAIL,
            EntityType.URL,
            EntityType.CURRENCY,  # Protect currency from acronym/abbreviation expansion
            EntityType.TEMPERATURE,
            EntityType.FRACTION,
            EntityType.X_KALI,
            EntityType.IC,
            EntityType.HARI_BULAN,
            EntityType.HIJRI,
        ]

        # Conditionally extract these based on config
        enabled_entities = []
        if config:
            # Only extract dates if enabled
            if config.is_enabled("dates"):  # type: ignore[arg-type]
                enabled_entities.append(EntityType.DATE)
            # Only extract times if enabled
            if config.is_enabled("times"):  # type: ignore[arg-type]
                enabled_entities.append(EntityType.TIME)
        else:
            # No config provided - extract all entities by default for entity extraction mode
            enabled_entities = [EntityType.DATE, EntityType.TIME]

        # Combine always + conditionally extracted entities
        entities_to_extract = enabled_entities + always_extract

        # Phase 1: Extract entities and apply pronunciation mappings
        extractor = EntityExtractor()
        protected_text, entities = extractor.extract(text, entities_to_extract)

        # Apply pronunciation mappings BEFORE processing non-entity text
        # This ensures terms like "JSON" → "jay son" and preserves acronyms like "ML"
        protected_text = apply_pronunciation_mappings(protected_text, effective_language)

        # Phase 2: Process non-entity text (text quality features only, NO basic normalization)
        # Basic normalization will be applied to entities during restoration

        # Normalize spacing (if enabled)
        spacing_enabled = True
        if config:
            spacing_enabled = config.is_enabled("spacing")  # type: ignore[arg-type]
        if spacing_enabled:
            protected_text = normalize_whitespace(protected_text)

        # Remove sound words
        sound_words_field = ""
        if config:
            sound_words_field = "\n".join(config.sound_words)
        if sound_words_field and sound_words_field.strip():
            sound_words = parse_sound_word_field(sound_words_field)
            if sound_words:
                protected_text = smart_remove_sound_words(protected_text, sound_words)

        # Expand abbreviations (if enabled)
        abbreviations_enabled = True
        if config:
            abbreviations_enabled = config.is_enabled("abbreviations")  # type: ignore[arg-type]
        if abbreviations_enabled:
            protected_text = expand_abbreviations(protected_text, effective_language)

        # Expand acronyms (if enabled)
        acronyms_enabled = True
        if config:
            acronyms_enabled = config.is_enabled("acronyms")  # type: ignore[arg-type]
        if acronyms_enabled:
            protected_text = replace_letter_period_sequences(protected_text, process_acronyms=True)

        # Insert comma after repeated words
        protected_text = insert_comma_after_repeated_words(protected_text, min_repeat=3)

        # Normalize measurements (distance, volume, weight, duration)
        # These need to be processed on protected text to avoid interfering with entity placeholders
        from revo_norm.malaya_inspired_utils import normalize_measurements, normalize_x_kali_text
        protected_text = normalize_measurements(protected_text, effective_language)

        # Normalize x-kali multiplier notation (10x, 5x, etc.)
        # This should happen after measurements to avoid conflicts (e.g., "10x km")
        protected_text = normalize_x_kali_text(protected_text, effective_language)

        # Phase 3: Restore entities as spoken form
        # Entities get converted directly without going through basic normalizer
        result = extractor.restore(protected_text, effective_language)

        # Remove preservation markers from pronunciation mappings
        result = remove_preservation_markers(result)

        return result

    except Exception as e:
        # If entity extraction fails, fall back to legacy approach
        import logging

        logging.warning(f"Entity extraction failed: {e}. Falling back to legacy normalization.")
        # Return original text (normalized or not)
        # Don't recursively call normalize_text
        return text
