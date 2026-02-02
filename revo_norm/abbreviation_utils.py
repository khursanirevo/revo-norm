"""
Abbreviation and short form expansion utilities for text normalization.

This module provides mappings for common abbreviations and short forms
that should be expanded to their full spoken form for TTS applications.
"""

import re
from typing import Dict

# English abbreviations and short forms
ABBREVIATIONS_EN: Dict[str, str] = {
    # Units of measurement - length
    "km": "kilometer",
    "km2": "square kilometer",
    "km3": "cubic kilometer",
    "kms": "kilometers",
    "m": "meter",
    "m2": "square meter",
    "m3": "cubic meter",
    "cm": "centimeter",
    "cm2": "square centimeter",
    "cm3": "cubic centimeter",
    "cms": "centimeters",
    "mm": "millimeter",
    "mm2": "square millimeter",
    "mm3": "cubic millimeter",
    "mms": "millimeters",
    "um": "micrometer",
    "nm": "nanometer",
    "ft": "foot",
    "fts": "feet",
    "in": "inch",
    "ins": "inches",
    "yd": "yard",
    "yds": "yards",
    "mi": "mile",
    "mis": "miles",
    "nmi": "nautical mile",
    "nmis": "nautical miles",
    # Weight
    "kg": "kilogram",
    "kgs": "kilograms",
    "g": "gram",
    "gs": "grams",
    "mg": "milligram",
    "mgs": "milligrams",
    "ug": "microgram",
    "ugs": "micrograms",
    "ng": "nanogram",
    "ngs": "nanograms",
    "lb": "pound",
    "lbs": "pounds",
    "oz": "ounce",
    "ozs": "ounces",
    "t": "ton",
    "ts": "tons",
    # Volume
    "l": "liter",
    "ls": "liters",
    "ml": "milliliter",
    "mls": "milliliters",
    "cl": "centiliter",
    "cls": "centiliters",
    "dl": "deciliter",
    "dls": "deciliters",
    "gal": "gallon",
    "gals": "gallons",
    "qt": "quart",
    "qts": "quarts",
    "pt": "pint",
    "pts": "pints",
    "floz": "fluid ounce",
    "flozs": "fluid ounces",
    # Temperature (c for celsius, f for fahrenheit, k for kelvin)
    "degc": "celsius",
    "degf": "fahrenheit",
    "degk": "kelvin",
    # Speed
    "kph": "kilometers per hour",
    "kmh": "kilometers per hour",
    "km/h": "kilometers per hour",
    "mph": "miles per hour",
    "mps": "meters per second",
    "knot": "knot",
    "knots": "knots",
    # Data
    "b": "byte",
    "bs": "bytes",
    "kb": "kilobyte",
    "kbs": "kilobytes",
    "mb": "megabyte",
    "mbs": "megabytes",
    "gb": "gigabyte",
    "gbs": "gigabytes",
    "tb": "terabyte",
    "tbs": "terabytes",
    "pb": "petabyte",
    "pbs": "petabytes",
    "eb": "exabyte",
    "ebs": "exabytes",
    # Time
    "s": "second",
    "secs": "seconds",
    "ms": "millisecond",
    "msec": "millisecond",
    "msecs": "milliseconds",
    "us": "microsecond",
    "usec": "microsecond",
    "usecs": "microseconds",
    "ns": "nanosecond",
    "nsec": "nanosecond",
    "nsecs": "nanoseconds",
    "min": "minute",
    "mins": "minutes",
    "hr": "hour",
    "hrs": "hours",
    "wk": "week",
    "wks": "weeks",
    "mo": "month",
    "mos": "months",
    "yr": "year",
    "yrs": "years",
    # Math and science
    "sqrt": "square root",
    "sq": "square",
    "cu": "cubic",
    "eq": "equation",
    "eqs": "equations",
    "calc": "calculate",
    "calcs": "calculates",
    "calculation": "calculation",
    "formula": "formula",
    "formulas": "formulas",
    "func": "function",
    "funcs": "functions",
    "var": "variable",
    "vars": "variables",
    "const": "constant",
    "consts": "constants",
    "param": "parameter",
    "params": "parameters",
    "arg": "argument",
    "args": "arguments",
    "num": "number",
    "nums": "numbers",
    "denom": "denominator",
    "denoms": "denominators",
    "coeff": "coefficient",
    "coeffs": "coefficients",
    "exp": "exponent",
    "exps": "exponents",
    "log": "logarithm",
    "logs": "logarithms",
    "ln": "natural logarithm",
    "sin": "sine",
    "cos": "cosine",
    "tan": "tangent",
    "csc": "cosecant",
    "cot": "cotangent",
    "arcsin": "inverse sine",
    "arccos": "inverse cosine",
    "arctan": "inverse tangent",
    "asin": "inverse sine",
    "acos": "inverse cosine",
    "atan": "inverse tangent",
    "sinh": "hyperbolic sine",
    "cosh": "hyperbolic cosine",
    "tanh": "hyperbolic tangent",
    "derivative": "derivative",
    "integral": "integral",
    "matrix": "matrix",
    "matrices": "matrices",
    "vector": "vector",
    "vectors": "vectors",
    "tensor": "tensor",
    "tensors": "tensors",
    "prob": "probability",
    "stats": "statistics",
    "stddev": "standard deviation",
    "variance": "variance",
    "median": "median",
    "mode": "mode",
    "range": "range",
    # Computing and programming
    "app": "application",
    "apps": "applications",
    "prog": "program",
    "progs": "programs",
    "dev": "developer",
    "devs": "developers",
    "ops": "operations",
    "db": "database",
    "dbs": "databases",
    # Note: Acronyms (API, SDK, GUI, CLI, CPU, GPU, RAM, ROM, SSD, HDD, USB, etc.)
    # are handled by expand_capitalized_initialisms() in text_normalizer.py
    # They are NOT included here to avoid double-processing and allow proper flag control
    "os": "operating system",
    "oss": "operating systems",
    # Network protocols (not acronyms - spoken as words)
    "tcp": "T C P",
    "udp": "U D P",
    "ssh": "S S H",
    "ssl": "S S L",
    "tls": "T L S",
    "dhcp": "D H C P",
    "nat": "N A T",
    # Data formats (spoken as words, not letter-by-letter)
    "json": "jay-son",
    "xml": "X M L",
    "html": "H T M L",
    "css": "C S S",
    "js": "J S",
    "sql": "S Q L",
    "nosql": "no S Q L",
    "git": "git",
    "github": "git hub",
    "gitlab": "git lab",
    "svn": "S V N",
    "unix": "unix",
    "linux": "linux",
    "ubuntu": "ubuntu",
    "debian": "debian",
    "centos": "cent o s",
    "redhat": "red hat",
    "windows": "windows",
    "macos": "mac o s",
    "ios": "i o s",
    "android": "android",
    # Internet and web
    "www": "w w w",
    "url": "u r l",
    "urls": "u r l s",
    "ftp": "f t p",
    "smtp": "s m t p",
    "pop3": "p o p three",
    "imap": "i m a p",
    "isp": "i s p",
    "isps": "i s p s",
    # Common business/organization terms
    "dept": "department",
    "depts": "departments",
    "div": "division",
    "divs": "divisions",
    "corp": "corporation",
    "corps": "corporations",
    "inc": "incorporated",
    "llc": "l l c",
    "ltd": "limited",
    "co": "company",
    "ceo": "c e o",
    "cto": "c t o",
    "cfo": "c f o",
    "coo": "c o o",
    "cio": "c i o",
    "qa": "q a",
    "qc": "q c",
    "kpi": "k p i",
    "kpis": "k p i s",
    "roi": "r o i",
    "rois": "r o i s",
    "crm": "c r m",
    "erp": "e r p",
    # Education and academic
    "edu": "education",
    "univ": "university",
    "univs": "universities",
    "prof": "professor",
    "profs": "professors",
    "asst": "assistant",
    "assoc": "associate",
    "lect": "lecturer",
    "lects": "lecturers",
    "grad": "graduate",
    "undergrad": "undergraduate",
    "do": "d o",
    "rn": "r n",
    "lpn": "l p n",
    "pa": "p a",
    # Misc
    "etc": "etcetera",
    "vs": "versus",
    "aka": "also known as",
    "asap": "as soon as possible",
    "atm": "at the moment",
    "diy": "do it yourself",
    "faq": "f a q",
    "faqs": "f a q s",
    "fyi": "for your information",
    "tba": "to be announced",
    "tbd": "to be determined",
    "tbc": "to be confirmed",
    "lol": "l o l",
    "omg": "o m g",
    "wtf": "w t f",
    "btw": "by the way",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "ff": "following",
    "eg": "for example",
    "ie": "that is",
    "st": "saint",
    "mt": "mount",
}


# Malay abbreviations and short forms
ABBREVIATIONS_MS: Dict[str, str] = {
    # Units of measurement - length
    "km": "kilometer",
    "km2": "kilometer persegi",
    "km3": "kilometer padu",
    "kms": "kilometer",
    "m": "meter",
    "m2": "meter persegi",
    "m3": "meter padu",
    "cm": "sentimeter",
    "cm2": "sentimeter persegi",
    "cm3": "sentimeter padu",
    "cms": "sentimeter",
    "mm": "milimeter",
    "mm2": "milimeter persegi",
    "mm3": "milimeter padu",
    "mms": "milimeter",
    "um": "mikrometer",
    "nm": "nanometer",
    "ft": "kaki",
    "fts": "kaki",
    "in": "inci",
    "ins": "inci",
    "yd": "ela",
    "yds": "ela",
    "mi": "batu",
    "mis": "batu",
    # Weight
    "kg": "kilogram",
    "kgs": "kilogram",
    "g": "gram",
    "gs": "gram",
    "mg": "miligram",
    "mgs": "miligram",
    "lb": "paun",
    "lbs": "paun",
    "oz": "auns",
    "ozs": "auns",
    # Volume
    "l": "liter",
    "ls": "liter",
    "ml": "mililiter",
    "mls": "mililiter",
    "gal": "gelen",
    "gals": "gelen",
    "qt": "kuart",
    "qts": "kuart",
    "pt": "pik",
    "pts": "pik",
    # Temperature
    "degc": "celcius",
    "degf": "fahrenheit",
    "degk": "kelvin",
    # Speed
    "kph": "kilometer sejam",
    "kmh": "kilometer sejam",
    "km/h": "kilometer sejam",
    "mph": "batu sejam",
    "mps": "meter saat",
    "knot": "knot",
    "knots": "knot",
    # Data
    "b": "bait",
    "bs": "bait",
    "kb": "kilobait",
    "kbs": "kilobait",
    "mb": "megabait",
    "mbs": "megabait",
    "gb": "gigabait",
    "gbs": "gigabait",
    "tb": "terabait",
    "tbs": "terabait",
    "pb": "petabait",
    "pbs": "petabait",
    # Time
    "s": "saat",
    "secs": "saat",
    "ms": "milisaat",
    "msec": "milisaat",
    "msecs": "milisaat",
    "min": "minit",
    "mins": "minit",
    "hr": "jam",
    "hrs": "jam",
    "wk": "minggu",
    "wks": "minggu",
    "mo": "bulan",
    "mos": "bulan",
    "yr": "tahun",
    "yrs": "tahun",
    # Math and science
    "sqrt": "punca kuasa dua",
    "sq": "persegi",
    "cu": "padu",
    "eq": "persamaan",
    "eqs": "persamaan",
    "calc": "kira",
    "calcs": "kira",
    "formula": "formula",
    "formulas": "formula",
    "func": "fungsi",
    "funcs": "fungsi",
    "var": "pembolehubah",
    "vars": "pembolehubah",
    "const": "pemalar",
    "consts": "pemalar",
    "param": "parameter",
    "params": "parameter",
    "num": "nombor",
    "nums": "nombor",
    "denom": "penyebut",
    "denoms": "penyebut",
    "coeff": "pekali",
    "coeffs": "pekali",
    "exp": "eksponen",
    "exps": "eksponen",
    "log": "logaritma",
    "logs": "logaritma",
    "ln": "logaritma asli",
    "sin": "sinus",
    "tan": "tangen",
    "derivative": "terbitan",
    "integral": "kamiran",
    "matrix": "matriks",
    "matrices": "matriks",
    "vector": "vektor",
    "vectors": "vektor",
    "prob": "kebarangkalian",
    "stats": "statistik",
    "stddev": "sisihan piawai",
    "variance": "varians",
    "median": "median",
    "mode": "mod",
    "range": "julat",
    # Computing and programming
    "app": "aplikasi",
    "apps": "aplikasi",
    "prog": "program",
    "progs": "program",
    "dev": "pembangun",
    "devs": "pembangun",
    "ops": "operasi",
    "db": "pangkalan data",
    "dbs": "pangkalan data",
    # Note: Acronyms (API, SDK, GUI, CLI, CPU, GPU, RAM, ROM, SSD, HDD, USB, etc.)
    # are handled by expand_capitalized_initialisms() in text_normalizer.py
    # They are NOT included here to avoid double-processing and allow proper flag control
    "os": "sistem pengendalian",
    # Network protocols (spoken as words)
    "tcp": "T C P",
    "udp": "U D P",
    "ssh": "S S H",
    "ssl": "S S L",
    "tls": "T L S",
    # Data formats (spoken as words, not letter-by-letter)
    "json": "jay-son",
    "xml": "X M L",
    "html": "H T M L",
    "css": "C S S",
    "js": "J S",
    "sql": "S Q L",
    "git": "git",
    "github": "git hub",
    "linux": "linux",
    "windows": "windows",
    # Common business/organization terms
    "dept": "jabatan",
    "depts": "jabatan",
    "div": "bahagian",
    "divs": "bahagian",
    "corp": "perbadanan",
    "corps": "perbadanan",
    "inc": "ditubuhkan",
    "ltd": "terhad",
    "co": "syarikat",
    "ceo": "c e o",
    "cto": "c t o",
    "cfo": "c f o",
    "coo": "c o o",
    "qa": "q a",
    "qc": "q c",
    "kpi": "k p i",
    "kpis": "k p i",
    "roi": "r o i",
    "rois": "r o i",
    "crm": "c r m",
    "erp": "e r p",
    # Education and academic
    "edu": "pendidikan",
    "univ": "universiti",
    "univs": "universiti",
    "prof": "profesor",
    "profs": "profesor",
    "asst": "penolong",
    "assoc": "bersekutu",
    "lect": "pensyarah",
    "lects": "pensyarah",
    "grad": "siswazah",
    "undergrad": "pra-siswazah",
    # Misc
    "etc": "dan sebagainya",
    "vs": "lawan",
    "aka": "juga dikenali sebagai",
    "asap": "secepat mungkin",
    "atm": "pada masa ini",
    "diy": "buat sendiri",
    "faq": "s o a l",
    "faqs": "s o a l",
    "fyi": "untuk makluman anda",
    "tba": "akan diumumkan",
    "tbd": "akan ditentukan",
    "tbc": "akan disahkan",
    "btw": "secara kebetulan",
    "imo": "pada pendapat saya",
    "imho": "pada pendapat saya yang tawaduk",
    "ff": "berikut",
    "eg": "contohnya",
    "ie": "iaitu",
    "st": "saint",
    "mt": "gunung",
}


# Create regex patterns for abbreviation matching
# These patterns match abbreviations as whole words, optionally preceded by a number
_ABBREVIATION_PATTERN_EN = re.compile(
    r"(?<![\w\.])(%s)(?![\w\.])"
    % "|".join(re.escape(abbr) for abbr in sorted(ABBREVIATIONS_EN.keys(), key=len, reverse=True)),
    re.IGNORECASE,
)

_ABBREVIATION_PATTERN_MS = re.compile(
    r"(?<![\w\.])(%s)(?![\w\.])"
    % "|".join(re.escape(abbr) for abbr in sorted(ABBREVIATIONS_MS.keys(), key=len, reverse=True)),
    re.IGNORECASE,
)


def expand_abbreviations(text: str, language: str = "en") -> str:
    """
    Expand abbreviations and short forms in text.

    Note: Single-letter abbreviations are NOT expanded to avoid breaking
    domain terms like "ML", "LLM", "meter L", etc. Only abbreviations
    with 2+ characters are expanded.

    Args:
        text: Input text containing abbreviations
        language: Language code ('en' for English, 'ms' for Malay)

    Returns:
        Text with abbreviations expanded to their full form

    Example:
        >>> expand_abbreviations("The speed is 100 km/h", language="en")
        'The speed is 100 kilometer/h'
        >>> expand_abbreviations("Hitung sqrt dari 25", language="ms")
        'Hitung punca kuasa dua dari 25'
    """
    if language == "en":
        pattern = _ABBREVIATION_PATTERN_EN
        mappings = ABBREVIATIONS_EN
    elif language == "ms":
        pattern = _ABBREVIATION_PATTERN_MS
        mappings = ABBREVIATIONS_MS
    else:
        # Unknown language, return text as-is
        return text

    def replace_abbr(match):
        abbr = match.group(0)

        # Skip single-letter abbreviations (too ambiguous, breaks domain terms)
        # This prevents "L" in "ML", "LLM" from being expanded to "liter"
        if len(abbr) <= 1:
            # Exception: Allow if preceded by a number (e.g., "5m", "2.3B", "10K")
            start = match.start()
            # Look back up to 10 characters for a number
            preceding_text = text[max(0, start - 10):start].strip()
            # Check if preceding text ends with a digit (number notation)
            if preceding_text and preceding_text[-1].isdigit():
                # This is likely number notation (5m, 2.3B, 10K), allow expansion
                pass
            else:
                # Single letter not preceded by number - skip it
                return abbr

        # Skip short all-uppercase abbreviations (likely acronyms)
        # These are typically domain terms: ML, AI, API, CPU, GPU, RAM, etc.
        if len(abbr) <= 3 and abbr.isupper() and abbr.isalpha():
            return abbr

        # Preserve case by looking up the lowercase version
        return mappings.get(abbr.lower(), abbr)

    return pattern.sub(replace_abbr, text)


def get_abbreviation_mapping(language: str = "en") -> Dict[str, str]:
    """
    Get the abbreviation mapping dictionary for a language.

    Args:
        language: Language code ('en' for English, 'ms' for Malay)

    Returns:
        Dictionary mapping abbreviations to their full forms
    """
    if language == "en":
        return ABBREVIATIONS_EN.copy()
    elif language == "ms":
        return ABBREVIATIONS_MS.copy()
    else:
        return {}


def add_custom_abbreviation(abbr: str, full_form: str, language: str = "en") -> None:
    """
    Add a custom abbreviation to the mapping.

    Note: This modifies the global mapping dictionary. The new abbreviation
    will be used in all subsequent calls to expand_abbreviations().

    Args:
        abbr: The abbreviation (e.g., 'abbr')
        full_form: The full spoken form (e.g., 'abbreviation')
        language: Language code ('en' for English, 'ms' for Malay)

    Example:
        >>> add_custom_abbreviation('abbr', 'abbreviation', language='en')
        >>> expand_abbreviations('Use the abbr button', language='en')
        'Use the abbreviation button'
    """
    global _ABBREVIATION_PATTERN_EN, _ABBREVIATION_PATTERN_MS

    if language == "en":
        ABBREVIATIONS_EN[abbr.lower()] = full_form
        # Recompile pattern with new abbreviation
        _ABBREVIATION_PATTERN_EN = re.compile(
            r"(?<![\w\.])(%s)(?![\w\.])"
            % "|".join(
                re.escape(a) for a in sorted(ABBREVIATIONS_EN.keys(), key=len, reverse=True)
            ),
            re.IGNORECASE,
        )
    elif language == "ms":
        ABBREVIATIONS_MS[abbr.lower()] = full_form
        # Recompile pattern with new abbreviation
        _ABBREVIATION_PATTERN_MS = re.compile(
            r"(?<![\w\.])(%s)(?![\w\.])"
            % "|".join(
                re.escape(a) for a in sorted(ABBREVIATIONS_MS.keys(), key=len, reverse=True)
            ),
            re.IGNORECASE,
        )
