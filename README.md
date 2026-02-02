# Revo Norm

Text normalization library for English and Malay TTS applications.

## Installation

From PyPI:
```bash
pip install revo-norm
```

From source:
```bash
git clone https://github.com/yourusername/revo-norm.git
cd revo-norm
pip install -e .
```

## Quick Start

```python
from revo_norm import normalize_text

# English
result = normalize_text("Meeting at 3:30 pm on 15/08/2025", language="en")
print(result)
# "Meeting at three thirty pm on fifteenth of August two thousand and twenty-five"

# Malay
result = normalize_text("Jumpa 2:30 petang pada 12/03/2025", language="ms")
print(result)
# "Jumpa dua tiga puluh petang pada dua belas Mac dua ribu dua puluh lima"
```

## Usage

```python
from revo_norm import normalize_text

# Basic usage
result = normalize_text("Price: RM100.50", language="en")

# With options
result = normalize_text(
    "Email user@example.com for info",
    language="en",
    normalize_spacing=True,
    sound_words_field="[laughter]\\n[applause]"
)

# With abbreviation expansion (default: enabled)
result = normalize_text("Speed: 100 km/h", language="en")
# "Speed: one hundred kilometer/h"

# Disable abbreviation expansion
result = normalize_text("Speed: 100 km/h", language="en", expand_abbreviations_flag=False)
# "Speed: one hundred km/h"
```

## API

| Function | Description |
|----------|-------------|
| `normalize_text(text, language='en')` | Main normalization function |
| `normalize_text(text, language='en', expand_abbreviations_flag=True)` | With abbreviation expansion toggle |
| `normalize_english(text)` | English normalization |
| `normalize_malay(text)` | Malay normalization |
| `email_to_spoken(email)` | Email to spoken form |
| `expand_capitalized_initialisms(text)` | Expand acronyms |
| `expand_abbreviations(text, language='en')` | Expand abbreviations and short forms |
| `get_abbreviation_mapping(language='en')` | Get abbreviation dictionary |
| `add_custom_abbreviation(abbr, full_form, language='en')` | Add custom abbreviation |

## Abbreviation Expansion

The library automatically expands common abbreviations and short forms:

**English examples:**
- `km` → `kilometer`
- `sqrt` → `square root`
- `kg` → `kilogram`
- `etc` → `etcetera`
- `vs` → `versus`

**Malay examples:**
- `km` → `kilometer`
- `sqrt` → `punca kuasa dua`
- `kg` → `kilogram`
- `dll` → `dan lain-lain` (planned)

Disable automatic expansion:
```python
normalize_text("100 km", language="en", expand_abbreviations_flag=False)
```

Add custom abbreviations:
```python
from revo_norm import add_custom_abbreviation
add_custom_abbreviation("abbr", "abbreviation", language="en")
```

## Running Tests

```bash
uv run pytest
```

## License

MIT
