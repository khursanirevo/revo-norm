"""
Standard Chinese text normalization for TTS.

Handles numbers, percentages, and decimals in standard Chinese (普通话) spoken
form. Dates, times, currency, temperature, and measurements are handled by
entity extraction and shared_features (which respect config flags).
"""

import re

from revo_norm.num2word_zh import to_cardinal, to_year

# Month names (used by entity_extractor for Chinese dates)
_MONTHS = {
    "01": "一月", "1": "一月",
    "02": "二月", "2": "二月",
    "03": "三月", "3": "三月",
    "04": "四月", "4": "四月",
    "05": "五月", "5": "五月",
    "06": "六月", "6": "六月",
    "07": "七月", "7": "七月",
    "08": "八月", "8": "八月",
    "09": "九月", "9": "九月",
    "10": "十月",
    "11": "十一月",
    "12": "十二月",
}

_percentage_re = re.compile(r"\b(\d+(?:\.\d+)?)%")
_decimal_re = re.compile(r"\b(\d+)\.(\d+)\b")
_number_re = re.compile(r"\b\d+\b")
_number_with_commas_re = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")

# Measurement unit → Chinese (used by shared_features for Chinese measurements)
_MEASUREMENT_UNITS = {
    "km": "公里",
    "m": "米",
    "cm": "厘米",
    "mm": "毫米",
    "kg": "公斤",
    "g": "克",
    "mg": "毫克",
    "ml": "毫升",
    "l": "升",
    "litre": "升",
    "liter": "升",
}

_measurement_re = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(km|m|cm|mm|kg|g|mg|ml|l|litre|liter)\b",
    re.IGNORECASE,
)


def _num_to_day(n: int) -> str:
    """Convert day number to Chinese spoken form for dates."""
    if n <= 0 or n > 31:
        return to_cardinal(n)
    if n == 10:
        return "十"
    if n < 10:
        return to_cardinal(n)
    if n < 20:
        return f"十{to_cardinal(n % 10)}"
    if n % 10 == 0:
        return f"{to_cardinal(n // 10)}十"
    return f"{to_cardinal(n // 10)}十{to_cardinal(n % 10)}"


def _num_to_month(n: int) -> str:
    """Convert month number to Chinese month name."""
    return _MONTHS.get(str(n), to_cardinal(n) + "月")


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


def normalize_measurement(m: re.Match) -> str:
    value = m.group(1)
    unit = m.group(2).lower()
    unit_word = _MEASUREMENT_UNITS.get(unit, unit)
    if "." in value:
        dec_words = normalize_decimal(re.match(r"(\d+)\.(\d+)", value))
        return f"{dec_words}{unit_word}"
    return f"{to_cardinal(int(float(value)))}{unit_word}"


def normalize_number(m: re.Match) -> str:
    num_str = m.group(0)
    num = int(num_str)
    if len(num_str) == 4 and 1000 <= num <= 2099:
        return to_year(num)
    return to_cardinal(num)


def normalize_number_with_commas(m: re.Match) -> str:
    num_str = m.group(0).replace(",", "")
    return to_cardinal(int(num_str))


def text_normalize_zh(text: str) -> str:
    """Main Chinese text normalization function."""
    text = re.sub(_percentage_re, normalize_percentage, text)
    text = re.sub(_decimal_re, normalize_decimal, text)
    text = re.sub(_number_with_commas_re, normalize_number_with_commas, text)
    text = re.sub(_number_re, normalize_number, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
