"""
Standard Chinese text normalization for TTS.

Handles numbers, currency, dates, times, measurements, temperature,
percentages, and decimals in standard Chinese (普通话) spoken form.
"""

import re

from revo_norm.currency_utils import CURRENCY_K_SUFFIX_PATTERN, expand_currency_k_suffix
from revo_norm.num2word_zh import to_cardinal, to_year

# Currency symbol → Chinese unit name
_CURRENCY_UNITS = {
    "RM": "令吉",
    "MYR": "令吉",
    "$": "美元",
    "USD": "美元",
    "£": "英镑",
    "GBP": "英镑",
    "€": "欧元",
    "EUR": "欧元",
    "¥": "元",
    "RMB": "元",
    "CNY": "元",
    "JPY": "日元",
}

# Month names
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

# Regex patterns
_currency_k_re = CURRENCY_K_SUFFIX_PATTERN

_currency_re = re.compile(
    r"(?<!\w)(RM|\$|£|€|USD|EUR|GBP|MYR|JPY|CNY|RMB|¥)"
    r"\s?([\d,]+(?:[\.,]\d{1,2})?)"
    r"(?:\s+(million|billion|trillion|thousand|万|亿))?\b",
    re.IGNORECASE,
)

_date_re = re.compile(r"\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{2,4})\b")
_date_ymd_re = re.compile(r"\b(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})\b")
_time_re = re.compile(
    r"\b(\d{1,2}):(\d{2})\s*(?:(am|pm|a\.m\.|p\.m\.|上午|下午))",
    re.IGNORECASE,
)
_time_no_meridian_re = re.compile(
    r"\b(\d{1,2}):(\d{2})\b(?!\s*(?:am|pm|a\.m\.|p\.m\.|上午|下午))(?!.*%)",
    re.IGNORECASE,
)
_percentage_re = re.compile(r"\b(\d+(?:\.\d+)?)%")
_decimal_re = re.compile(r"\b(\d+)\.(\d+)\b")
_number_re = re.compile(r"\b\d+\b")
_number_with_commas_re = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")
_temperature_re = re.compile(r"\b(\d+(?:\.\d+)?)\s*°?\s*[Cc]\b")
_measurement_re = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(km|m|cm|mm|kg|g|mg|ml|l|litre|liter)\b",
    re.IGNORECASE,
)

# Measurement unit → Chinese
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
    if hour_int == 12 and minute_int == 0:
        return "中午十二点"

    if minute_int == 0:
        return f"{to_cardinal(hour_int)}点"
    return f"{to_cardinal(hour_int)}点{to_cardinal(minute_int)}分"


def normalize_currency(m: re.Match) -> str:
    symbol = m.group(1).upper()
    amount = m.group(2).replace(",", "")
    magnitude = (m.group(3) or "").strip() or None

    unit = _CURRENCY_UNITS.get(symbol, "元")

    if magnitude:
        mag_map = {"thousand": "千", "million": "百万", "billion": "十亿", "trillion": "兆", "万": "万", "亿": "亿"}
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


def normalize_temperature(m: re.Match) -> str:
    temp = m.group(1)
    return f"{to_cardinal(float(temp))}摄氏度"


_DECIMAL_PART_RE = re.compile(r"(\d+)\.(\d+)")


def normalize_measurement(m: re.Match) -> str:
    value = m.group(1)
    unit = m.group(2).lower()
    unit_word = _MEASUREMENT_UNITS.get(unit, unit)
    if "." in value:
        dec_match = _DECIMAL_PART_RE.match(value)
        dec_words = normalize_decimal(dec_match) if dec_match else value
        return f"{dec_words}{unit_word}"
    return f"{to_cardinal(int(float(value)))}{unit_word}"


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


def text_normalize_zh(text: str) -> str:
    """Main Chinese text normalization function."""
    text = re.sub(_currency_k_re, expand_currency_k_suffix, text)

    text = re.sub(_date_ymd_re, normalize_date_ymd, text)
    text = re.sub(_date_re, normalize_date, text)
    text = re.sub(_currency_re, normalize_currency, text)
    text = re.sub(_time_no_meridian_re, normalize_time_no_meridian, text)
    text = re.sub(_time_re, normalize_time, text)
    text = re.sub(_temperature_re, normalize_temperature, text)
    text = re.sub(_measurement_re, normalize_measurement, text)
    text = re.sub(_percentage_re, normalize_percentage, text)
    text = re.sub(_decimal_re, normalize_decimal, text)
    text = re.sub(_number_with_commas_re, normalize_number_with_commas, text)
    text = re.sub(_number_re, normalize_number, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
