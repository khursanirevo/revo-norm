# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Revo Norm** is a Python library for text normalization designed for Text-to-Speech (TTS) applications. It converts written text into spoken form for English and Malay (Bahasa Melayu) languages.

## Development Commands

```bash
# Install from source (development mode)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Run tests (when tests exist)
uv run pytest

# Run tests with coverage
uv run pytest --cov

# Format code
black revo_norm tests

# Lint code
flake8 revo_norm tests

# Type check
mypy revo_norm
```

## Architecture

The library follows an **entity-aware normalization pipeline** - it identifies and processes specific text entities (URLs, emails, dates, times, currency, numbers) rather than applying whole-text transformations.

### Core Components

- **`revo_norm/text_normalizer.py`**: Main orchestrator containing `normalize_text()` and shared utilities (email/URL conversion, acronym expansion, sound word removal)
- **`revo_norm/normalizer_en.py`**: English-specific normalization (contractions, abbreviations, entity-aware date/time/currency processing using `inflect`)
- **`revo_norm/normalizer_ms.py`**: Malay-specific normalization with custom number-to-words implementation
- **`revo_norm/currency_utils.py`**: Entity-aware currency K-suffix expansion (RM30K → RM30000)
- **`revo_norm/num2word.py`**: Pure Malay number-to-words conversion (cardinal, ordinal, currency, year formats)

### Normalization Pipeline Order

The order of operations in `normalize_text()` is critical:

1. **Currency K-suffix expansion** (e.g., RM30K → RM30000) - MUST be first to avoid breaking URL patterns
2. **URL/Email conversion** - must happen before general dot/slash processing
3. **Pronunciation overrides** (applied twice)
4. **Language-specific normalization** (`normalizer_en` or `normalizer_ms`)
5. **Sound word removal** (optional)
6. **Acronym expansion**
7. **Spacing normalization**
8. **Letter period sequence handling** (I.B.M. → I B M)
9. **Special character replacement**

### Key Design Patterns

- **Entity-specific regex patterns**: URL regex requires protocol/www prefix to avoid matching currency (e.g., "RM1.5K")
- **Language-agnostic utilities**: `currency_utils.py` provides universal currency patterns for both languages
- **Modular language support**: Each language has its own normalizer with shared base utilities

## Project Status

- **Version**: 0.1.0 (Alpha)
- **Recent transition**: Replaced LLM-based normalization with rule-based approach
- **Tests**: Configured but no test files currently exist
