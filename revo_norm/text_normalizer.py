import re
import string
from typing import List, Tuple, Optional

from revo_norm.normalizer_en import text_normalize as text_normalizer_en
from revo_norm.normalizer_ms import normalize_malay as text_normalizer_ms
from revo_norm.currency_utils import expand_currency_k_suffix, CURRENCY_K_SUFFIX_PATTERN
from revo_norm.abbreviation_utils import expand_abbreviations


def normalize_whitespace(text: str) -> str:
    """Normalize multiple whitespace to single space and strip."""
    return re.sub(r'\s{2,}', ' ', text.strip())


def email_to_spoken(email: str) -> str:
    """
    Convert an email address into a spoken-friendly form for TTS.

    Example:
        'sugumaran_thiagarajan@yahoo.com'
        -> 'sugumaran underscore thiagarajan at yahoo dot com'
    """
    spoken = email.replace("@", " at ")
    # Replace all dots with " dot " (not just .com)
    spoken = spoken.replace(".", " dot ")
    spoken = spoken.replace("_", " underscore ")
    spoken = spoken.replace("+", " plus ")
    # Replace hyphen with " dash " in emails
    spoken = spoken.replace("-", " dash ")

    return re.sub(r"\s+", " ", spoken).strip()


# Email regex pattern
_EMAIL_RE = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    re.IGNORECASE
)


def convert_emails_to_spoken(text: str) -> str:
    """
    Find all email addresses in text and convert them to spoken form using regex.
    This prevents messing up dots in other parts of the text.
    """
    def replace_email(match):
        email = match.group(0)
        return email_to_spoken(email)

    return _EMAIL_RE.sub(replace_email, text)


def url_to_spoken(url: str) -> str:
    """
    Convert a URL/website into a spoken-friendly form for TTS.

    Examples:
        'www.google.com' -> 'w w w dot google dot com'
        'http://192.168.1.1:8080/path' -> 'h t t p colon slash slash one nine two...'
    """
    spoken = url

    # Replace protocol FIRST (before touching numbers)
    spoken = re.sub(r'https?://', 'h t t p colon slash slash ', spoken)
    spoken = re.sub(r'ftp://', 'f t p colon slash slash ', spoken)

    # Replace www
    spoken = re.sub(r'www\.?', 'w w w dot ', spoken)

    # Handle port numbers separately (before general processing)
    def replace_port(match):
        port = match.group(1)
        port_digits = ' '.join(list(port))
        return f' colon {port_digits}'
    spoken = re.sub(r':(\d+)', replace_port, spoken)

    # Replace remaining dots with " dot "
    spoken = spoken.replace(".", " dot ")

    # Replace slashes with " slash "
    spoken = spoken.replace("/", " slash ")

    # Replace remaining numbers with digit-by-digit speaking (for IP addresses)
    def speak_number_digits(match):
        num = match.group(0)
        return ' '.join(list(num))

    spoken = re.sub(r'\d+', speak_number_digits, spoken)

    # Replace hyphens with " dash "
    spoken = spoken.replace("-", " dash ")

    # Clean up extra spaces
    spoken = re.sub(r'\s+', ' ', spoken).strip()

    return spoken


# URL regex pattern - matches www., http://, https://, ftp://, IPs, domains, and ports
# Entity-specific: Requires protocol/www OR stricter domain pattern to avoid matching currency (RM1.5K)
_URL_RE = re.compile(
    r'(?:https?://|ftp://|www\.)[^\s]+|'  # Protocol-based URLs (must start with protocol/www)
    r'\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/[^\s]*)?|'  # IP addresses
    r'\b[A-Za-z0-9-]+\.[A-Za-z]{2,}(?:/[^\s]*)?',  # Simple domains (e.g., example.com)
    re.IGNORECASE
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


def replace_letter_period_sequences(text: str) -> str:
    """Replace letter period sequences like 'I.B.M.' with 'I B M'."""
    def replacer(match):
        cleaned = match.group(0).rstrip('.')
        letters = cleaned.split('.')
        return ' '.join(letters)
    return re.sub(r'\b(?:[A-Za-z]\.){2,}', replacer, text)


def remove_inline_reference_numbers(text: str) -> str:
    """Remove reference numbers after punctuation (e.g., 'word1.' -> 'word.')."""
    pattern = r'([.!?,\\\'"\)\]])(\d+)(?=\s|$)'
    return re.sub(pattern, r'\1', text)


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


def expand_capitalized_initialisms(text: str) -> str:
    """Expand capitalized acronyms in text."""
    def replacer(match):
        acronym = match.group(0)
        return expand_acronym(acronym)
    return re.sub(r'\b([A-Z]{2,})\b', replacer, text)


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using basic regex."""
    sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z])')
    return [s.strip() for s in sentence_endings.split(text) if s.strip()]


def parse_sound_word_field(user_input: str) -> List[Tuple[str, str]]:
    """Parse sound word field input into list of (pattern, replacement) tuples."""
    lines = [l.strip() for l in user_input.split('\n') if l.strip()]
    result = []
    for line in lines:
        if '=>' in line:
            pattern, replacement = line.split('=>', 1)
            result.append((pattern.strip(), replacement.strip()))
        else:
            result.append((line, ''))
    return result


def smart_remove_sound_words(text: str, sound_words: List[Tuple[str, str]]) -> str:
    """Remove or replace sound words like [laughter], [applause] from text."""
    for pattern, replacement in sound_words:
        if replacement:
            text = re.sub(
                r'(?i)(%s)([' r"'\u2019`s?])" % re.escape(pattern),
                lambda m: replacement + "'s" if m.group(2) else replacement,
                text
            )
            if all(char in "-—-" for char in pattern.strip()):
                text = re.sub(re.escape(pattern), replacement, text)
            else:
                text = re.sub(
                    r'\b%s\b' % re.escape(pattern),
                    replacement,
                    text,
                    flags=re.IGNORECASE
                )
        else:
            text = re.sub(
                r'%s' % re.escape(pattern),
                '',
                text,
                flags=re.IGNORECASE
            )

    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([,\s]+,)+', ',', text)
    text = re.sub(r',\s*,+', ',', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = re.sub(r'(\s+,|,\s+)', ', ', text)
    text = re.sub(r'(^|[\.!\?]\s*),+', r'\1', text)
    text = re.sub(r',+\s*([\.!\?])', r'\1', text)
    return text.strip()


def insert_comma_after_repeated_words(text: str, min_repeat: int = 3) -> str:
    """Insert comma after repeated words (e.g., 'test test test test' -> 'test test test, test')."""
    pattern = r'\b(?P<word>\w+)\b(?: \1){' + str(min_repeat) + r',}'

    def replacer(match):
        phrase = match.group(0)
        words = phrase.split()
        return ' '.join(words[:-1]) + ', ' + words[-1]

    return re.sub(pattern, replacer, text, flags=re.IGNORECASE)


def apply_pronunciation_overrides(text: str) -> str:
    """Apply pronunciation overrides for specific words and phrases."""
    text = re.sub(r'\btwenty-three\b', 'twenty tree', text, flags=re.IGNORECASE)
    text = re.sub(r'\bthree\b', 'three', text, flags=re.IGNORECASE)
    text = re.sub(r'\btwenty-eight\b', 'twenty, eight', text, flags=re.IGNORECASE)
    text = re.sub(r'\bcut-off\b', 'kad off', text, flags=re.IGNORECASE)
    text = re.sub(r'\beighty-eight\b', 'eighty eight', text, flags=re.IGNORECASE)
    text = re.sub(r'\bNumber\b', 'number', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba/l\b', 'anak lelaki', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba/p\b', 'anak perempuan', text, flags=re.IGNORECASE)
    text = re.sub(r'\b1Malaysia\b', 'satu malaysia', text, flags=re.IGNORECASE)
    text = re.sub(r'\bNo\.\b', 'number', text, flags=re.IGNORECASE)
    # Don't replace "/" here - let date regex handle dates like 12/03/2025

    unit_map = {
        "mg": "milligram",
        "kg": "kilogram",
        "GB": "gigabyte",
        "hb": "haribulan"
    }

    for unit, spoken in unit_map.items():
        pattern = rf'(\d+)\s*{unit}\b'
        text = re.sub(pattern, rf'\1 {spoken}', text, flags=re.IGNORECASE)

    return text


def special_replace(text: str, language: str = 'en') -> str:
    """
    Special character and punctuation normalization.
    This function replaces special characters with spoken equivalents.
    """
    # Language-specific replacements
    percent_word = 'percent' if language == 'en' else 'peratus'

    replacements = {
        '&': 'and',
        '+': 'plus',
        '=': 'equals',
        '@': 'at',
        '#': 'hash',
        '*': 'star',
        '%': percent_word,
        '$': 'dollar',
        'EUR': 'euro',
        'GBP': 'pound',
        '©': 'copyright',
        '®': 'registered',
        '™': 'trademark',
        '<': 'less than',
        '>': 'greater than',
        '|': 'bar',
        '~': 'tilde',
        '^': 'caret',
    }

    for char, replacement in replacements.items():
        text = text.replace(char, f' {replacement} ')

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_text(
    text: str,
    language: str = 'en',
    normalize_spacing: bool = True,
    fix_dot_letters: bool = True,
    sound_words_field: str = "",
    apply_pronunciation_overrides_flag: bool = True,
    expand_abbreviations_flag: bool = True,
) -> str:
    """
    Main text normalization function.

    Args:
        text: The input text to normalize
        language: Language code ('en' for English, 'ms' for Malay)
        normalize_spacing: Whether to normalize whitespace
        fix_dot_letters: Whether to fix letter period sequences
        sound_words_field: Sound words to remove (newline-separated, use '=>' for replacements)
        apply_pronunciation_overrides_flag: Whether to apply pronunciation overrides
        expand_abbreviations_flag: Whether to expand abbreviations and short forms (default: True)

    Returns:
        Normalized text string
    """
    text = text.strip()
    if not text or len(text) == 0:
        return ""

    # Expand currency with K suffix FIRST (before URL/email conversion)
    # This ensures RM30K becomes RM30000 before URL processing breaks it
    text = CURRENCY_K_SUFFIX_PATTERN.sub(lambda m: expand_currency_k_suffix(m), text)

    # Convert URLs and emails (after K expansion to avoid breaking currency patterns)
    # This prevents IP addresses in URLs from being processed as decimals
    text = convert_urls_to_spoken(text)
    text = convert_emails_to_spoken(text)

    # Apply pronunciation overrides
    if apply_pronunciation_overrides_flag:
        text = apply_pronunciation_overrides(text)

    # Language-specific normalization
    if language == 'en':
        text = text_normalizer_en(text)
    elif language == 'ms':
        text = text_normalizer_ms(text)

    # Remove sound words
    if sound_words_field and sound_words_field.strip():
        sound_words = parse_sound_word_field(sound_words_field)
        if sound_words:
            text = smart_remove_sound_words(text, sound_words)

    # Expand abbreviations and short forms (e.g., km -> kilometer, sqrt -> square root)
    if expand_abbreviations_flag:
        text = expand_abbreviations(text, language)

    # Expand acronyms
    text = expand_capitalized_initialisms(text)

    # Normalize spacing
    if normalize_spacing:
        text = normalize_whitespace(text)

    # Fix letter period sequences
    if fix_dot_letters:
        text = replace_letter_period_sequences(text)

    # Apply pronunciation overrides again
    if apply_pronunciation_overrides_flag:
        text = apply_pronunciation_overrides(text)

    # Insert comma after repeated words
    text = insert_comma_after_repeated_words(text, min_repeat=3)

    # Apply special character replacements
    text = special_replace(text, language)

    return text
