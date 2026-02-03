# Revo Norm

**A comprehensive text normalization library designed specifically for Text-to-Speech (TTS) applications, supporting English and Malay (Bahasa Melayu).**

> **⚠️ IMPORTANT:** This library is designed for **TTS (text → speech)** normalization ONLY. It is **NOT suitable for ASR (speech → text)** preprocessing. The normalization transforms text into its spoken form, which is inappropriate for speech recognition systems.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-green.svg)
[![Tests](https://img.shields.io/badge/tests-149-brightgreen.svg)
[![Coverage](https://img.shields.io/badge/coverage-66%25-brightgreen.svg)

## Features

- ✅ **Language Support**: English and Malay (Bahasa Melayu)
- ✅ **TTS-Specific Design**: For text-to-speech only, NOT for ASR preprocessing
- ✅ **18+ Normalization Features**: Currency, URLs, emails, dates, times, temperature, IC numbers, measurements, fractions, pronunciation mappings
- ✅ **Smart Configuration**: Profile-based configuration (minimal, basic, standard, aggressive, technical_doc)
- ✅ **Entity Extraction**: Prevents pattern conflicts via 3-phase approach
- ✅ **Pronunciation Mappings**: JSON → "jay son", tech acronyms preserved (ML, AI, API)
- ✅ **149 Tests**: Comprehensive test coverage with 66% code coverage
- ✅ **Modern Tooling**: Uses uv, ruff, pytest for fast development

## Installation

### From PyPI

```bash
pip install revo-norm
```

### From Source (using uv - Recommended)

```bash
git clone https://github.com/yourusername/revo-norm.git
cd revo-norm
uv sync --all-extras
```

### From Source (using pip)

```bash
git clone https://github.com/yourusername/revo-norm.git
cd revo-norm
pip install -e ".[dev]"
```

## Quick Start

> **⚠️ NOT FOR ASR:** This library normalizes text for **TTS (text → speech)**. It converts written text into spoken form (e.g., "RM100" → "seratus ringgit"). **DO NOT use** for ASR (speech → text) preprocessing.

```python
from revo_norm import normalize_text

```python
from revo_norm import normalize_text

# English example
result = normalize_text("Meeting at 3:30 pm on 15/08/2025", language="en")
print(result)
# "Meeting at three thirty pm on fifteenth of August two thousand and twenty-five"

# Malay example
result = normalize_text("Jumpa 2:30 petang pada 12/03/2025", language="ms")
print(result)
# "Jumpa dua tiga puluh petang pada dua belas Mac dua ribu dua puluh lima"

# With entity extraction (experimental - fixes date/fraction conflicts)
result = normalize_text(
    "On 15/08/2025 we completed 3/4 of the work",
    language="en",
    extract_entities_first=True
)
print(result)
# "on fifteenth of August two thousand and twenty-five we completed three over four of the work"
```

## Normalization Features

### How It Works

The library uses **two different approaches** for text normalization:

| Approach | Description | Use Case |
|----------|-------------|----------|
| **Legacy Pipeline** (default) | Rule-based processing with strict ordering | General use, production |
| **Entity Extraction** (experimental) | 3-phase: extract → process → restore | Complex text, pattern conflicts |

### Core Features

| Category | Features | Example Transformations |
|----------|----------|--------------------------|
| **Currency** | K-suffix expansion | `RM30K` → `RM30000` |
| **Entities** | URLs, emails, dates, times | `user@example.com` → `user at example dot com` |
| **Malay-Specific** | IC, Hari Bulan, Hijri, X-Kali | `911111-01-1111` → digit-by-digit |
| **Measurements** | Temperature, distance, weight | `25C` → `twenty five celsius` |
| **Text Quality** | Spacing, abbreviations, acronyms | `I'm` → `I am`, `API` → `A P I` |

### Feature Profiles

| Profile | Description | Best For |
|---------|-------------|----------|
| `minimal` | Basic cleanup only | Well-formatted text |
| `basic` | Standard normalization | Conversations, emails |
| `standard` | Full normalization (default) | News, articles, formal text |
| `aggressive` | Maximum normalization | Social media, informal text, OCR |
| `technical_doc` | Preserves acronyms | Technical documentation |

## Usage

### Basic Usage

```python
from revo_norm import normalize_text

# Simple usage
result = normalize_text("Price: RM100.50", language="en")

# With sound word removal
result = normalize_text(
    "Hello [laughter], this is a test",
    language="en",
    sound_words_field="[laughter]\n[applause]"
)
```

### Configuration System (Recommended)

```python
from revo_norm import normalize_text, standard_config, FeatureGroup, FeatureLevel

# Use preset profile
result = normalize_text("25C outside", language="en", profile="aggressive")

# Use custom config
config = standard_config()
config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
result = normalize_text("The API is fast", language="en", config=config)
```

### Legacy API (Backward Compatible)

```python
# Disable specific features
result = normalize_text(
    "The API is fast, 25C outside",
    language="en",
    normalize_temperature_flag=False,
    expand_abbreviations_flag=False,
)
```

### Entity Extraction Mode (Experimental)

```python
# Fixes pattern conflicts (e.g., date vs fraction)
result = normalize_text(
    "On 15/08/2025 we completed 3/4 of the work",
    language="en",
    extract_entities_first=True
)
```

## Examples

### Email Normalization (Language-Aware)

```python
# English
normalize_text("Email user@example.com", language="en")
# "user at example dot com"

# Malay
normalize_text("Email user@example.com", language="ms")
# "user di example dot com"
```

### Date and Time Normalization

```python
# With entity extraction (recommended for dates/times)
from revo_norm import normalize_text

text = "Meeting on 15/08/2025 at 3:30 pm"
result = normalize_text(text, language="en", extract_entities_first=True)
# "meeting on fifteenth of august two thousand and twenty-five at three thirty p m"
```

### Temperature Normalization

```python
normalize_text("It's 25C today", language="en")
# "it is twenty five celsius today"

normalize_text("Suhu 30C di luar", language="ms")
# "suhu tiga puluh celcius di luar"
```

### Currency K-Suffix Expansion

```python
normalize_text("Budget RM30K for project", language="en")
# "Budget thirty thousand ringgit for project"
```

## ⚠️ Important: TTS-Specific Design

### Purpose

This library is designed **exclusively for Text-to-Speech (TTS) applications**. It normalizes written text into its **spoken form**, which is essential for TTS systems but **inappropriate for ASR (Automatic Speech Recognition)**.

### What It Does (TTS)

The library transforms text for **speech synthesis**:

| Input | Output | Purpose |
|-------|--------|---------|
| `RM100` | `seratus ringgit` | Convert written form to spoken form |
| `25°C` | `twenty five celsius` | Pronounceable symbols |
| `3:30 pm` | `three thirty p m` | Spoken time format |
| `user@example.com` | `user at example dot com` | Expand abbreviations |
| `JSON` | `jay son` | Correct pronunciation |
| `ML` | `ML` (preserved) | Acronym preservation |

### Why NOT for ASR

**DO NOT use this library for ASR preprocessing** because:

1. ❌ **It destroys information needed for ASR**
   - "RM100" → "seratus ringgit" loses the original format
   - ASR needs to preserve original text structure

2. ❌ **It adds tokens that confuse ASR**
   - Expands: "API" → "A P I", "JSON" → "jay son"
   - Converts numbers: "123" → "one two three"
   - This makes ASR transcription harder

3. ❌ **Wrong direction for speech processing**
   - TTS: text → spoken form ✅
   - ASR: audio → text (needs original format) ❌

### Use Case Compatibility

| Application | Use Revo Norm? | Reason |
|-------------|---------------|---------|
| **TTS (Text → Speech)** | ✅ YES | Converts text to spoken form for synthesis |
| **ASR (Speech → Text)** | ❌ NO | Would corrupt text before recognition |
| **Translation Engines** | ❌ NO | Should preserve original format |
| **Chat Applications** | ❌ NO | Users need to see original text |
| **Voice Assistants** | ✅ YES | Prepares text for TTS output only |

### Example: Wrong Usage for ASR

```python
# ❌ WRONG: Using for ASR preprocessing
from revo_norm import normalize_text

# DON'T DO THIS for ASR!
transcript = "User spent RM100 on 5 items"
normalized = normalize_text(transcript, language="ms")
# Result: "user spent seratus ringgit on lima items"
# ASR receives corrupted text instead of original "RM100"
```

### Example: Correct Usage for TTS

```python
# ✅ CORRECT: Using for TTS
from revo_norm import normalize_text

# This is what it's designed for
text = "Harga RM100 untuk 5 unit"
normalized = normalize_text(text, language="ms")
# TTS will say: "harga seratus ringgit untuk lima unit"
# Perfect for speech synthesis!
```

## Development

### Setup

```bash
# Install development dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov
```

### Code Quality

```bash
# Format code (ruff)
uv run ruff format revo_norm/ tests/

# Check linting (ruff)
uv run ruff check revo_norm/ tests/

# Auto-fix linting issues
uv run ruff check --fix revo_norm/
```

### Project Tooling

- **uv** - Fast Python package manager (10-100x faster than pip)
- **ruff** - Fast linter and formatter (replaces flake8, black, isort)
- **pytest** - Testing framework with coverage

## Testing

```bash
# Run all tests (149 tests)
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest tests/test_normalization_comprehensive.py::TestTemperature::test_english_celsius -v
```

### Test Coverage

- **149 tests** covering all features
- **66% code coverage** (target: 80%+)
- Includes unit tests, integration tests, edge cases, and performance tests

## Architecture

### Pipeline Order (Legacy)

```
1. Currency K-suffix expansion (MUST BE FIRST)
2. Email conversion (with language support)
3. URL conversion
4. Malaya-inspired features (elongated, fractions, x-kali, temperature, IC, measurements)
5. Language-specific normalization (EN/MS)
6. Abbreviation and acronym expansion
7. Spacing normalization
8. Special character replacement
```

### Entity Extraction (Experimental)

```
1. Extract entities → replace with placeholders (<<<DATE_1>>>, <<<EMAIL_2>>>)
2. Process non-entity text safely
3. Restore entities as spoken form
```

### Key Design Decisions

1. **Currency K-suffix first**: Must happen before URL processing to avoid breaking patterns
2. **Emails before URLs**: Prevents URL pattern from matching email domains
3. **Hari bulan underscore**: `sepuluh_hari_bulan` → `sepuluh hari bulan` (prevents contractions)
4. **Malay email language**: `@` → "di" in Malay, `@` → "at" in English

## Project Status

- **Version**: 0.2.0-dev (Alpha)
- **Python**: 3.9+
- **Tests**: 149 passing
- **Coverage**: 66%
- **Scope**: TTS text normalization only (NOT for ASR)
- **State**: Feature-complete for v0.2.0

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass (`uv run pytest`)
6. Format code (`uv run ruff format`)
7. Submit a pull request

## Documentation

- **DEVELOPMENT.md** - Development guide with tooling details
- **CLAUDE.md** - Developer guidance for Claude Code

## Changelog

### 0.2.0-dev (Current)
- Added Malay email language support (`@` → "di" in Malay)
- Fixed 8 major pipeline contradictions
- Implemented configuration system with profiles
- Implemented entity extraction system (experimental)
- Added 58 new tests (123 total)
- Improved test coverage to 81%
- Migrated to modern tooling (uv, ruff)
- Cleaned up documentation files

### 0.1.0
- Initial release with Malaya-inspired features
- Abbreviation expansion library
- Currency K-suffix expansion

## Support

For issues, questions, or suggestions, please open an issue on GitHub repository.
