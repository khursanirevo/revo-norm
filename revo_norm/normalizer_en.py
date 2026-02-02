import re
import inflect

_inflect = inflect.engine()

# Import shared currency utilities (language-agnostic)
from revo_norm.currency_utils import expand_currency_k_suffix, CURRENCY_K_SUFFIX_PATTERN

# Mappings
numbers_mapping_en = {
    '0': 'zero', '1': 'one', '2': 'two', '3': 'three',
    '4': 'four', '5': 'five', '6': 'six', '7': 'seven',
    '8': 'eight', '9': 'nine', '+': 'plus'
}

contractions_en = [
    (re.compile(r"\b%s\b" % re.escape(x[0]), re.IGNORECASE), x[1])
    for x in [
        ("I'm", "I am"), ("I've", "I have"), ("I'll", "I will"), ("I'd", "I would"),
        ("you're", "you are"), ("you've", "you have"), ("you'll", "you will"), ("you'd", "you would"),
        ("he's", "he is"), ("he'll", "he will"), ("he'd", "he would"),
        ("she's", "she is"), ("she'll", "she will"), ("she'd", "she would"),
        ("it's", "it is"), ("it'll", "it will"), ("it'd", "it would"),
        ("we're", "we are"), ("we've", "we have"), ("we'll", "we will"), ("we'd", "we would"),
        ("they're", "they are"), ("they've", "they have"), ("they'll", "they will"), ("they'd", "they would"),
        ("that's", "that is"), ("that'll", "that will"), ("that'd", "that would"),
        ("there's", "there is"), ("there'll", "there will"), ("there'd", "there would"),
        ("who's", "who is"), ("who'll", "who will"), ("who'd", "who would"),
        ("what's", "what is"), ("what'll", "what will"), ("what'd", "what would"),
        ("where's", "where is"), ("where'll", "where will"), ("where'd", "where would"),
        ("when's", "when is"), ("when'll", "when will"), ("when'd", "when would"),
        ("why's", "why is"), ("why'll", "why will"), ("why'd", "why would"),
        ("how's", "how is"), ("how'll", "how will"), ("how'd", "how would"),
        ("isn't", "is not"), ("aren't", "are not"), ("wasn't", "was not"), ("weren't", "were not"),
        ("hasn't", "has not"), ("haven't", "have not"), ("hadn't", "had not"),
        ("doesn't", "does not"), ("don't", "do not"), ("didn't", "did not"),
        ("won't", "will not"), ("wouldn't", "would not"), ("shan't", "shall not"),
        ("shouldn't", "should not"), ("can't", "cannot"), ("couldn't", "could not"),
        ("mustn't", "must not"),
        ("should've", "should have"), ("would've", "would have"), ("could've", "could have"),
        ("shall've", "shall have"), ("will've", "will have"), ("might've", "might have"),
        ("must've", "must have")
    ]
]

abbreviations_en = [
    (re.compile("\\b%s\\." % x[0], re.IGNORECASE), x[1])
    for x in [
        ("mrs", "misess"),
        ("mr", "mister"),
        ("dr", "doctor"),
        ("st", "saint"),
        ("co", "company"),
        ("jr", "junior"),
        ("maj", "major"),
        ("gen", "general"),
        ("drs", "doctors"),
        ("rev", "reverend"),
        ("lt", "lieutenant"),
        ("hon", "honorable"),
        ("sgt", "sergeant"),
        ("capt", "captain"),
        ("esq", "esquire"),
        ("ltd", "limited"),
        ("col", "colonel"),
        ("ft", "fort"),
    ]
]
months_en = {
    '01': 'January', '1': 'January', '02': 'February', '2': 'February',
    '03': 'March', '3': 'March', '04': 'April', '4': 'April',
    '05': 'May', '5': 'May', '06': 'June', '6': 'June',
    '07': 'July', '7': 'July', '08': 'August', '8': 'August',
    '09': 'September', '9': 'September', '10': 'October',
    '11': 'November', '12': 'December'
}

# Regex patterns
# Use shared currency K suffix pattern from currency_utils
_currency_k_re = CURRENCY_K_SUFFIX_PATTERN

_currency_re = re.compile(r'(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR)\s?([\d,]+(?:[\.,]\d{1,2})?)\b', re.IGNORECASE)
_percentage_re = re.compile(r'\b(\d+(?:\.\d+)?)%')
_decimal_re = re.compile(r'\b(\d+)\.(\d+)\b')
_dashed_digit_re = re.compile(r'(?<![A-Za-z])([+\d]+(?:-[\d]+)+)(?![A-Za-z])')
_ordinal_re = re.compile(r'\b(\d{1,2})(st|nd|rd|th)\b', re.IGNORECASE)
_mixed_alnum_re = re.compile(r'\b(?=\w*\d)(?=\w*[A-Za-z])[\w\-]+\b')
_number_re = re.compile(r'\b\d+\b')
_number_with_commas_re = re.compile(r'\b\d{1,3}(?:,\d{3})+\b')
_date_re = re.compile(r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\b')
_time_re = re.compile(r'\b(\d{1,2})[:\.](\d{2})\s*(?:(am|pm|a\.m\.|p\.m\.))', re.IGNORECASE)
_time_no_meridian_re = re.compile(r'\b(\d{1,2})[:\.](\d{2})\b(?!\s*(?:am|pm|a\.m\.|p\.m\.))(?!.*%)', re.IGNORECASE)

# Create ignore words set
IGNORE_WORDS = set()
for i in range(1, 32):
    IGNORE_WORDS.add(_inflect.number_to_words(i))
    ordinal_word = _inflect.number_to_words(_inflect.ordinal(i))
    IGNORE_WORDS.add(ordinal_word)


def normalize_mixed_alnum(m):
    token = m.group(0)
    if token.lower() in IGNORE_WORDS:
        return token
    return ' '.join(numbers_mapping_en.get(c, c.upper()) for c in token if c.isalnum())


def normalize_time(m):
    hour, minute, meridian = m.groups()
    hour_word = _inflect.number_to_words(int(hour))
    minute_word = _inflect.number_to_words(int(minute))

    meridian_word = ''
    if meridian:
        meridian_word = f"{meridian[0]} m"

    if minute_word == 'zero':
        return f"{hour_word} {meridian_word}".strip()
    else:
        return f"{hour_word} {minute_word} {meridian_word}".strip()


def normalize_time_no_meridian(m):
    """Normalize time without meridian (e.g., 17:30, 09:00)."""
    hour, minute = m.groups()
    hour_int = int(hour)
    minute_int = int(minute)

    # Special case for midnight (00:00)
    if hour_int == 0 and minute_int == 0:
        return "midnight"
    # Special case for noon (12:00)
    if hour_int == 12 and minute_int == 0:
        return "noon"

    hour_word = _inflect.number_to_words(hour_int)
    minute_word = _inflect.number_to_words(minute_int)

    if minute_word == 'zero':
        return hour_word
    else:
        return f"{hour_word} {minute_word}"


def expand_contractions(text, lang="en"):
    if lang == "en":
        _contractions = contractions_en
    else:
        raise NotImplementedError()
    for regex, replacement in _contractions:
        text = re.sub(regex, replacement, text)
    return text


def expand_abbreviations(text, lang="en"):
    if lang == "en":
        _abbreviations = abbreviations_en
    else:
        raise NotImplementedError()
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


def is_mixed_alnum(token):
    return any(c.isalpha() for c in token) and any(c.isdigit() for c in token)


def is_only_digits_and_dashes(token):
    return all(c.isdigit() or c in '+-' for c in token.replace('-', ''))


def normalize_date(m):
    day, month, year = m.groups()
    month_name = months_en.get(month.lstrip('0'), month)
    day_word = _inflect.number_to_words(_inflect.ordinal(int(day)))
    year_word = _inflect.number_to_words(int(year), andword='and')
    return f"{day_word} of {month_name}, {year_word}"


def normalize_currency(m):
    symbol, amount = m.groups()
    amount = amount.replace(",", "")
    if symbol.upper() == 'RM':
        unit_main, unit_sub = 'ringgit', 'cent'
    elif symbol.upper() == 'MYR':
        unit_main, unit_sub = 'ringgit', 'cent'
    elif symbol == '$':
        unit_main, unit_sub = 'dollar', 'cent'
    elif symbol == '£':
        unit_main, unit_sub = 'pound', 'pence'
    elif symbol == '€':
        unit_main, unit_sub = 'euro', 'cent'
    elif symbol == 'USD':
        unit_main, unit_sub = 'dollar', 'cent'
    else:
        unit_main, unit_sub = 'unit', 'subunit'

    if '.' in amount:
        major, minor = amount.split('.')
        if minor != '00':
            return f"{_inflect.number_to_words(int(major))} {unit_main} {_inflect.number_to_words(int(minor[:2]))} {unit_sub}"
        else:
            return f"{_inflect.number_to_words(int(major))} {unit_main}"
    else:
        return f"{_inflect.number_to_words(int(amount))} {unit_main}"


def normalize_percentage(m):
    number = m.group(1)
    if '.' in number:
        whole, frac = number.split('.')
        frac_words = ' '.join(_inflect.number_to_words(int(digit)) for digit in frac)
        return f"{_inflect.number_to_words(int(whole))} point {frac_words} percent"
    else:
        return f"{_inflect.number_to_words(int(number))} percent"


def normalize_decimal(m):
    whole, frac = m.group(1), m.group(2)
    frac_words = ' '.join(_inflect.number_to_words(int(digit)) for digit in frac)
    return f"{_inflect.number_to_words(int(whole))} point {frac_words}"


def normalize_dashed_digits(m):
    raw = m.group(1)
    return ' '.join(numbers_mapping_en.get(ch, ch) if ch != '-' else 'dash' for ch in raw)


def normalize_ordinal(m):
    number = int(m.group(1))
    return _inflect.number_to_words(_inflect.ordinal(number))


def normalize_number(m):
    if len(m.group(0)) > 4:
        return ' '.join(_inflect.number_to_words(int(digit)) for digit in m.group(0))
    else:
        return _inflect.number_to_words(int(m.group(0)))


def normalize_number_with_commas(m):
    """Normalize numbers with commas like 1,000,000 or 7,832."""
    num_str = m.group(0).replace(',', '')
    num = int(num_str)
    return _inflect.number_to_words(num)


def text_normalize(text: str) -> str:
    """
    Main English text normalization function.

    Entity-aware approach: Detects and normalizes specific entities
    (currency, dates, times, etc.) rather than processing the whole text.

    Currency K-suffix (RM30K) is expanded to full numbers (RM30000)
    BEFORE main currency normalization.
    """
    # Step 1: Expand currency with K suffix (entity-aware preprocessing)
    # e.g., RM30K → RM30000, RM1.5K → RM1500
    text = re.sub(_currency_k_re, expand_currency_k_suffix, text)

    # Step 2: Process other entities
    text = re.sub(_date_re, normalize_date, text)
    text = re.sub(_currency_re, normalize_currency, text)
    text = re.sub(_time_no_meridian_re, normalize_time_no_meridian, text)
    text = re.sub(_time_re, normalize_time, text)
    text = re.sub(_percentage_re, normalize_percentage, text)
    text = re.sub(_decimal_re, normalize_decimal, text)
    text = re.sub(_dashed_digit_re, normalize_dashed_digits, text)
    text = re.sub(_ordinal_re, normalize_ordinal, text)
    text = re.sub(_number_with_commas_re, normalize_number_with_commas, text)
    text = re.sub(_number_re, normalize_number, text)
    text = re.sub(_mixed_alnum_re, normalize_mixed_alnum, text)
    text = expand_contractions(text)
    text = expand_abbreviations(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
