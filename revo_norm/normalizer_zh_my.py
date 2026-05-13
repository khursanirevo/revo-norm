"""
Malaysian Chinese text normalization for TTS.

Extends standard Chinese normalization with:
- Code-mixing support (CJK + Latin script in same sentence)
- Malaysian currency conventions (RM → 令吉, colloquial 块)
- Malaysian-specific terms and pronunciation
"""

import re

from revo_norm.normalizer_zh import (
    _CURRENCY_UNITS,
    _decimal_re,
    _num_to_day,
    _num_to_month,
    _number_re,
    _number_with_commas_re,
    _percentage_re,
)
from revo_norm.num2word_zh import to_cardinal, to_year

# Malaysian Chinese uses 令吉 for Ringgit Malaysia
_CURRENCY_UNITS_MY = {
    **_CURRENCY_UNITS,
    "RM": "令吉",
    "MYR": "令吉",
    "$": "块",  # colloquial Malaysian Chinese
    "USD": "美元",
}

_currency_re = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR|JPY|CNY|RMB|¥)"
    r"\s?([\d,]+(?:[\.,]\d{1,2})?)"
    r"(?:\s+(million|billion|trillion|thousand|万|亿|千))?\b",
    re.IGNORECASE,
)

_time_re = re.compile(
    r"\b(\d{1,2}):(\d{2})\s*(?:(am|pm|a\.m\.|p\.m\.|上午|下午))",
    re.IGNORECASE,
)
_time_no_meridian_re = re.compile(
    r"\b(\d{1,2}):(\d{2})\b(?!\s*(?:am|pm|a\.m\.|p\.m\.|上午|下午))(?!.*%)",
    re.IGNORECASE,
)

# CJK unified ideographs range — used for code-mixing detection
_CJK_RE = re.compile(r"[一-鿿㐀-䶿]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def _has_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def _has_latin(text: str) -> bool:
    return bool(_LATIN_RE.search(text))


def normalize_currency_my(m: re.Match) -> str:
    symbol = m.group(1).upper()
    amount = m.group(2).replace(",", "")
    magnitude = (m.group(3) or "").strip() or None

    unit = _CURRENCY_UNITS_MY.get(symbol, "元")

    if magnitude:
        mag_map = {"thousand": "千", "million": "百万", "billion": "十亿", "trillion": "兆", "万": "万", "亿": "亿", "千": "千"}
        mag_word = mag_map.get(magnitude, magnitude)
        if "." in amount:
            whole, frac = amount.split(".")
            frac_words = "".join(to_cardinal(int(d)) for d in frac)
            return f"{to_cardinal(int(whole))}点{frac_words}{mag_word}{unit}"
        return f"{to_cardinal(int(amount))}{mag_word}{unit}"

    if "." in amount:
        major, minor = amount.split(".")
        cents = int(minor[:2])
        if cents > 0:
            return f"{to_cardinal(int(major))}{unit}{to_cardinal(cents)}分"
        return f"{to_cardinal(int(major))}{unit}"
    return f"{to_cardinal(int(amount))}{unit}"


def normalize_percentage(m: re.Match) -> str:
    number = m.group(1)
    if "." in number:
        whole, frac = number.split(".")
        frac_words = "".join(to_cardinal(int(d)) for d in frac)
        return f"百分之{to_cardinal(int(whole))}点{frac_words}"
    return f"百分之{to_cardinal(int(float(number)))}"


def normalize_decimal(m: re.Match) -> str:
    whole, frac = m.group(1), m.group(2)
    frac_words = "".join(to_cardinal(int(d)) for d in frac)
    return f"{to_cardinal(int(whole))}点{frac_words}"


def normalize_date(m: re.Match) -> str:
    day, month, year = m.groups()
    year_word = to_year(int(year))
    month_word = _num_to_month(int(month))
    day_word = _num_to_day(int(day))
    return f"{year_word}年{month_word}{day_word}日"


def normalize_date_ymd(m: re.Match) -> str:
    year, month, day = m.groups()
    year_word = to_year(int(year))
    month_word = _num_to_month(int(month))
    day_word = _num_to_day(int(day))
    return f"{year_word}年{month_word}{day_word}日"


def normalize_time(m: re.Match) -> str:
    hour, minute, meridian = m.groups()
    hour_int = int(hour)
    minute_int = int(minute)

    meridian_word = ""
    if meridian:
        m_lower = meridian.lower()
        if m_lower in ("pm", "p.m.") or meridian == "下午":
            meridian_word = "下午"
        elif m_lower in ("am", "a.m.") or meridian == "上午":
            meridian_word = "上午"

    if minute_int == 0:
        time_str = f"{to_cardinal(hour_int)}点"
    else:
        time_str = f"{to_cardinal(hour_int)}点{to_cardinal(minute_int)}分"

    return f"{meridian_word}{time_str}".strip()


def normalize_time_no_meridian(m: re.Match) -> str:
    hour, minute = m.groups()
    hour_int = int(hour)
    minute_int = int(minute)

    if hour_int == 0 and minute_int == 0:
        return "零点"

    if minute_int == 0:
        return f"{to_cardinal(hour_int)}点"
    return f"{to_cardinal(hour_int)}点{to_cardinal(minute_int)}分"


def normalize_number(m: re.Match) -> str:
    num_str = m.group(0)
    num = int(num_str)
    if len(num_str) == 4 and 1000 <= num <= 2099:
        return to_year(num)
    if len(num_str) > 4:
        return to_cardinal(num)
    return to_cardinal(num)


def normalize_number_with_commas(m: re.Match) -> str:
    num_str = m.group(0).replace(",", "")
    return to_cardinal(int(num_str))


def text_normalize_zh_my(text: str) -> str:
    """Main Malaysian Chinese text normalization function.

    Handles code-mixed text (CJK + Latin) by applying Chinese normalization
    to the full text. Latin words (English/Malay) are preserved as-is since
    Malaysian Chinese speakers naturally code-mix.

    Dates, times, currency, temperature, and measurements are handled by
    entity extraction and malay_features (which respect config flags).
    """
    text = re.sub(_percentage_re, normalize_percentage, text)
    text = re.sub(_decimal_re, normalize_decimal, text)
    text = re.sub(_number_with_commas_re, normalize_number_with_commas, text)
    text = re.sub(_number_re, normalize_number, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
