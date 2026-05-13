"""
Malaysian Chinese text normalization for TTS.

Extends standard Chinese with:
- Code-mixing support (CJK + Latin script in same sentence)
- Colloquial currency ($ → 块 instead of 美元)

Dates, times, currency, temperature, and measurements are handled by
entity extraction and shared_features (which respect config flags).
"""

import re

from revo_norm.normalizer_zh import (
    _decimal_re,
    _number_re,
    _number_with_commas_re,
    _percentage_re,
)
from revo_norm.num2word_zh import to_cardinal, to_year

# CJK unified ideographs range — used for code-mixing detection
_CJK_RE = re.compile(r"[一-鿿㐀-䶿]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def _has_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def _has_latin(text: str) -> bool:
    return bool(_LATIN_RE.search(text))


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


def normalize_number(m: re.Match) -> str:
    num_str = m.group(0)
    num = int(num_str)
    if len(num_str) == 4 and 1000 <= num <= 2099:
        return to_year(num)
    return to_cardinal(num)


def normalize_number_with_commas(m: re.Match) -> str:
    num_str = m.group(0).replace(",", "")
    return to_cardinal(int(num_str))


def text_normalize_zh_my(text: str) -> str:
    """Main Malaysian Chinese text normalization function."""
    text = re.sub(_percentage_re, normalize_percentage, text)
    text = re.sub(_decimal_re, normalize_decimal, text)
    text = re.sub(_number_with_commas_re, normalize_number_with_commas, text)
    text = re.sub(_number_re, normalize_number, text)
    text = re.sub(r"\s+", " ", text).strip()
    return text
