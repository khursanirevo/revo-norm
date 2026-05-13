"""
Chinese number-to-words conversion for TTS.

Supports cardinal numbers from 0 to 10^16 (兆).
Handles special Chinese number conventions:
- 十 (10) not 一十
- 一百零一 (101)
- 两千 (2000 colloquial) is NOT used — formal 二千 is used for TTS clarity
"""

_DIGITS = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
_UNITS = ["", "十", "百", "千"]
_LARGE_UNITS = ["", "万", "亿", "兆"]


def to_cardinal(number: int | float) -> str:
    """Convert a number to Chinese cardinal words.

    Args:
        number: The number to convert (0 to 10^16).

    Returns:
        Chinese spoken form of the number.
    """
    if number < 0:
        return "负" + to_cardinal(abs(number))

    if isinstance(number, float):
        int_part = int(number)
        dec_part = str(number).split(".", 1)[1]
        int_words = to_cardinal(int_part)
        dec_words = " ".join(_DIGITS[int(d)] for d in dec_part)
        return f"{int_words}点{dec_words}"

    n = int(number)

    if n == 0:
        return "零"

    return _convert_integer(n)


def _convert_integer(n: int) -> str:
    """Convert a non-negative integer to Chinese words."""
    if n < 10:
        return _DIGITS[n]

    if n < 100:
        return _convert_tens(n)

    if n < 1000:
        return _convert_hundreds(n)

    if n < 10000:
        return _convert_thousands(n)

    return _convert_large(n)


def _convert_tens(n: int) -> str:
    """Convert 10-99."""
    tens = n // 10
    ones = n % 10
    if tens == 1:
        return "十" if ones == 0 else f"十{_DIGITS[ones]}"
    return f"{_DIGITS[tens]}十" if ones == 0 else f"{_DIGITS[tens]}十{_DIGITS[ones]}"


def _convert_hundreds(n: int) -> str:
    """Convert 100-999."""
    hundreds = n // 100
    remainder = n % 100
    result = f"{_DIGITS[hundreds]}百"
    if remainder == 0:
        return result
    if remainder < 10:
        return f"{result}零{_DIGITS[remainder]}"
    tens_digit = remainder // 10
    if tens_digit == 0:
        return f"{result}零{_convert_tens(remainder)}"
    return f"{result}{_convert_tens(remainder)}"


def _convert_thousands(n: int) -> str:
    """Convert 1000-9999."""
    thousands = n // 1000
    remainder = n % 1000
    result = f"{_DIGITS[thousands]}千"
    if remainder == 0:
        return result
    if remainder < 100:
        return f"{result}零{_convert_hundreds(remainder) if remainder >= 100 else _convert_tens(remainder) if remainder >= 10 else _DIGITS[remainder]}"
    return f"{result}{_convert_hundreds(remainder)}"


def _convert_large(n: int) -> str:
    """Convert numbers >= 10000 using 万, 亿, 兆 grouping."""
    if n >= 10**16:
        raise OverflowError(f"Number {n} is too large (max 10^16)")

    parts: list[str] = []
    unit_idx = 0

    while n > 0:
        group = n % 10000
        if group > 0:
            group_str = _convert_group_of_4(group)
            unit = _LARGE_UNITS[unit_idx]
            parts.append(f"{group_str}{unit}")
        n //= 10000
        unit_idx += 1

    return "".join(reversed(parts))


def _convert_group_of_4(n: int) -> str:
    """Convert a 1-4 digit number within a larger number."""
    if n < 10:
        return _DIGITS[n]
    if n < 100:
        return _convert_tens(n)
    if n < 1000:
        return _convert_hundreds(n)
    return _convert_thousands(n)


def to_year(year: int) -> str:
    """Convert a year to Chinese spoken form (digit by digit).

    Args:
        year: 4-digit year.

    Returns:
        Year spoken digit by digit: 2025 → 二零二五
    """
    return "".join(_DIGITS[int(d)] for d in str(abs(year)))


def to_currency(value: int | float, currency: str = "ringgit") -> str:
    """Convert a number to Chinese currency spoken form.

    Args:
        value: The amount.
        currency: Currency unit name (e.g. "令吉", "美元", "人民币").

    Returns:
        Currency amount in Chinese: 100 → 一百令吉
    """
    if isinstance(value, float):
        int_part = int(value)
        dec_str = f"{value:.2f}".split(".", 1)[1]
        cents = int(dec_str)
        if cents > 0:
            return f"{to_cardinal(int_part)}{currency}{to_cardinal(cents)}分"
        return f"{to_cardinal(int_part)}{currency}"
    return f"{to_cardinal(value)}{currency}"
