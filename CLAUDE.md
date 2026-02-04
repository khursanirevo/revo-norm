# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this codebase.

## Project Overview

**Revo Norm** is a Python library for text normalization designed for Text-to-Speech (TTS) applications. It converts written text into spoken form for English and Malay (Bahasa Melayu) languages.

## Development Commands

```bash
# Install from source (development mode)
uv sync

# Install with development dependencies
uv sync --all-extras

# Install specific dependency group
uv sync --group dev

# Run all tests
uv run pytest ../tests/revo-norm/

# Run specific test file
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py -v

# Run tests with coverage
uv run pytest ../tests/revo-norm/ --cov --cov-report=term-missing

# Run specific test
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py::TestTemperature::test_english_celsius -v

# Format code (ruff)
uv run ruff format revo_norm/

# Check linting issues (ruff)
uv run ruff check revo_norm/

# Type check (ty)
uv run ty revo_norm/

# Run with verbose output
uv run pytest ../tests/revo-norm/ -v --tb=short

# Auto-fix linting issues
uv run ruff check revovo_norm/ --fix

# Show what would be formatted (dry-run)
uv run ruff format --check revo_norm/ tests/
```

## Architecture Overview

The library provides two normalization approaches:

### 1. **Legacy Pipeline** (default, `normalize_text()`)
Rule-based entity-aware normalization with specific ordering requirements.

**Critical Pipeline Order:**
1. Currency K-suffix expansion (RM30K → RM30000) - MUST be first
2. URL/Email conversion (prevents IP address issues)
3. **Pronunciation mappings** (HIGHEST PRIORITY) - JSON → "jay son", ML → "ML" (preserved)
4. Pronunciation overrides (legacy)
5. Malaya-inspired features (elongated, fractions, x-kali, temperature, IC, measurements, hari bulan, hijri)
6. Language-specific normalization (EN/MS)
7. Abbreviation expansion
8. Acronym expansion
9. Spacing normalization
10. Special character replacement
11. **Remove preservation markers** (from pronunciation mappings)

### 2. **Entity Extraction Pipeline** (recommended, `extract_entities_first=True`)
3-phase approach to prevent pattern conflicts:
1. Extract entities → replace with `<<<TYPE_ID>>>` placeholders
2. Process text safely (no basic normalization to avoid placeholder interference)
3. Restore entities as spoken form

**Use case:** Fixes date/fraction conflict, provides order-independent processing.

## Code Architecture

### Core Modules

| Module | Purpose | Key Dependencies |
|--------|---------|-------------------|
| `text_normalizer.py` | Main orchestrator, shared utilities | All other modules |
| `normalizer_en.py` | English normalization (contractions, abbreviations) | `inflect` |
| `normalizer_ms.py` | Malay normalization (grammar, vocabulary) | Custom number-to-words |
| `entity_extractor.py` | Entity extraction system | All feature modules |
| `pronunciation_mappings.py` | Explicit pronunciation mappings (HIGHEST PRIORITY) | None |
| `malaya_inspired_utils.py` | Malaysian-specific features | None |
| `abbreviation_utils.py` | Short form expansion (EN/MS mappings) | None |
| `currency_utils.py` | Currency K-suffix expansion | None |
| `num2word.py` | Malay number-to-words conversion | None |
| `config.py` | Configuration system with profiles | None |

### Feature Organization

**Entity-Specific Features** (have dedicated regex patterns, safe to disable):
- URLs, Emails, IC Numbers, Dates (NEW), Times (NEW), Temperature, Fractions, X-Kali, Measurements, Hari Bulan, Hijri Years

**Global Features** (operate on entire text):
- Language-specific normalization, number normalization, elongated words, abbreviations, acronyms, spacing

### Configuration System

**Profiles** (preset configurations):
- `minimal`: Basic cleanup only
- `basic`: Standard normalization for conversations
- `standard`: Full normalization (default) for news/articles
- `aggressive`: Maximum normalization for social media

**Feature Groups** (logical groupings):
- `NUMBERS`, `ENTITIES`, `SPACING`, `MEASUREMENTS`, `MALAY_LOCAL`, `ABBREVIATIONS`, `ACRONYMS`, `ELONGATED`, `DATES` (NEW), `TIMES` (NEW)

### Critical Pipeline Dependencies

1. **Currency before URLs**: `RM30K` → `RM30000` must happen before URL processing
2. **Dates before Fractions**: Entity extraction prevents date/fraction pattern conflict
3. **Hari Bulan Underscore**: `sepuluh_hari_bulan` → `sepuluh hari bulan` (underscore prevents contraction)

### Known Issues & Workarounds

1. **Acronyms in Abbreviation List**: Fixed - removed 96 acronyms (API, CPU, RAM, etc.) from abbreviation list
2. **Date/Fraction Conflict**: Fixed in entity extraction mode
3. **Double Pronunciation Overrides**: Removed duplicate call
4. **Config System**: New API available, legacy flags still supported
5. **RM Currency Split to Meter**: Fixed - Use `extract_entities_first=True` to protect currency from transformations
6. **JSON/ML/AI Acronym Splitting**: Fixed - Pronunciation mappings applied FIRST prevent unwanted splitting

## Testing

> **NOTE:** Test cases are stored in the parent ChatterBox repository (private) to keep challenge data private.
> Test location: `../tests/revo-norm/` (relative to revo-norm directory)

### Test Structure
- `../tests/revo-norm/test_normalization_comprehensive.py` - 45 tests covering all features
- `../tests/revo-norm/test_entity_extraction.py` - 16 tests for entity extraction system
- `../tests/revo-norm/test_missing_coverage.py` - 26 tests for coverage gaps
- `../tests/revo-norm/test_pronunciation_mappings.py` - 19 tests for pronunciation mappings

### Running Tests

```bash
# Run all tests (from revo-norm directory)
uv run pytest ../tests/revo-norm/

# Run with coverage
uv run pytest ../tests/revo-norm/ --cov

# Run specific test class
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py::TestTemperature -v

# Run specific test
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py::TestTemperature::test_english_celsius -v

# Debug with verbose output
uv run pytest ../tests/revo-norm/ -v --tb=short
```

### Test Coverage
- Current: ~66% overall
- Malaya features: 80%
- English normalizer: 66%
- Goal: 80%+

### Quick Test Command for Development

```bash
# When modifying a feature, run its specific test class
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py::TestTemperature -v

# After changes, verify no regressions
uv run pytest ../tests/revo-norm/test_normalization_comprehensive.py
```

## Important Patterns

### Adding New Normalization Features

1. **Entity-specific feature**: Add to `entity_extractor.py` with:
   - Entity type in `EntityType` enum
   - Pattern compilation method
   - Extraction logic
   - Conversion in `_convert_entity_to_spoken()`

2. **Global feature**: Add to appropriate normalizer (`normalizer_en.py` or `normalizer_ms.py`)

3. **Config support**: Add feature group to `config.py` if needed

4. **Tests**: Add tests in `test_normalization_comprehensive.py`

### Pattern Matching Guidelines

- **Word boundaries**: Use `\b` carefully to avoid partial matches
- **Sort by length**: Sort regex alternatives by length (longest first) for overlapping patterns
- **Entity patterns**: Require specific prefixes (www, http://, @) to avoid false matches
- **Currency**: Match currency symbol + amount + K suffix

### Language-Specific Considerations

- **Code-mixing**: Common in Malaysian Malay text (English terms in Malay sentences)
- **Date formats**: DD/MM/YYYY, YYYY-MM-DD, DD Month YYYY
- **Islamic calendar**: Hijri years, hari bulan format
- **Government/official**: IC numbers, official document formats

## Implementation Notes

### Recently Fixed Issues (v0.2.0-dev)

1. **Acronym/Abbreviation Conflict**: Removed 96 acronyms from abbreviation list (api, cpu, ram, etc.)
2. **Date/Fraction Pattern Conflict**: Fixed negative lookahead in fraction pattern
3. **Double Pronunciation**: Removed duplicate `apply_pronunciation_overrides()` call
4. **Hari Bulan Underscore**: Changed placeholder to `__HARI_BULAN__` for robustness
5. **Acronym Expansion**: Merged `expand_capitalized_initialisms` into `replace_letter_period_sequences`
6. **Regex Compilation**: Pre-compiled 30+ patterns at module level
7. **Flag Behavior**: Documented that flags disable feature-specific processing only
8. **RM Currency Meter Issue**: Added currency entity extraction - use `extract_entities_first=True` to protect currency from cascading transformations
9. **Single-Letter Abbreviation Expansion**: Disabled single-letter and short uppercase abbreviation expansion to prevent breaking domain terms (ML, AI, LLM, meter L, etc.)
10. **JSON/ML/AI Acronym Splitting**: Added pronunciation mappings system - explicit mappings applied FIRST in pipeline prevent unwanted transformations

### Files Modified

- `revo_norm/abbreviation_utils.py` - Removed acronyms from abbreviation list, added single-letter/short uppercase abbreviation skipping
- `revo_norm/pronunciation_mappings.py` - NEW module for explicit pronunciation mappings (highest priority in pipeline)
- `revo_norm/malaya_inspired_utils.py` - Fixed fraction pattern, improved hari bulan
- `revo_norm/text_normalizer.py` - Merged acronym handling, pre-compiled patterns, added entity extraction, added pronunciation mappings pipeline
- `revo_norm/entity_extractor.py` - Added currency entity type and conversion
- `revo_norm/config.py` - Added DATES and TIMES feature groups
- `revo_norm/__init__.py` - Exported new classes
- `tests/test_pronunciation_mappings.py` - NEW test file for pronunciation mappings (19 tests)

### Entity Extraction System (Recommended)

The **entity extraction approach** (`extract_entities_first=True`) is now the recommended method for handling currency and other entities. This approach:

1. **Extracts entities** → replaces with `<<<TYPE_ID>>>` placeholders
2. **Processes text** safely (placeholders won't be touched by other transformations)
3. **Restores entities** as spoken form

**This prevents cascading transformations like:**
- "RM" → "R M" (acronym expansion) → "R meter" (abbreviation expansion)

**Recommended usage:**
```python
from revo_norm import normalize_text

# Pronunciation mappings applied automatically
result = normalize_text("Parse JSON file", language="en")
# Output: "Parse jay son file"

# Tech acronyms are preserved
result = normalize_text("Train ML model", language="en")
# Output: "Train ML model" (not "Train M L model")

# Use entity extraction for robust handling of currency/entities
result = normalize_text("RM 450000 for ML project", language="ms", extract_entities_first=True)
# Output: "empat ratus lima puluh ribu ringgit for ML project"

# Add custom pronunciation mappings
from revo_norm.pronunciation_mappings import add_custom_mapping
add_custom_mapping("YOLO", "you only live once", "en")
result = normalize_text("YOLO approach", language="en")
# Output: "you only live once approach"
```

### Configuration System (NEW)

**Recommended usage (without entity extraction):**
```python
from revo_norm import normalize_text, standard_config, FeatureGroup, FeatureLevel

# Simple (standard profile)
result = normalize_text("25C outside", language="en")

# With profile
result = normalize_text("25C outside", language="en", profile="aggressive")

# With custom config
config = standard_config()
config.with_feature(FeatureGroup.ACRONYMS, FeatureLevel.OFF)
result = normalize_text("The API is fast", language="en", config=config)

# With entity extraction (experimental, fixes date/fraction conflicts)
result = normalize_text("On 15/08/2025", language="en", extract_entities_first=True)
```

**Legacy API still supported:**
```python
result = normalize_text("Hello", language="en", normalize_temperature_flag=True)
```

### New Features (v0.2.0-dev)

1. **Date Recognition**: `15/08/2025` → "fifteenth of August two thousand and twenty-five"
2. **Time Recognition**: `3:30 pm` → "three thirty p m"
3. **Currency Entity Extraction**: `RM 450000` → "empat ratus lima puluh ribu ringgit" (protected from acronym/abbreviation expansion)
4. **Pronunciation Mappings System**: Explicit mappings applied FIRST in pipeline
   - `JSON` → "jay son" (not "J S O N")
   - `GUI` → "gooey" (not "G U I")
   - `ML` → "ML" (preserved, not split)
   - `AI` → "AI" (preserved, not split)
   - Custom mappings can be added via `add_custom_mapping()`
5. **Entity Extraction System**: Prevents pattern conflicts via 3-phase approach
6. **Configuration Profiles**: `minimal`, `basic`, `standard`, `aggressive`
7. **Feature Groups**: Organized features (NUMBERS, ENTITIES, DATES, TIMES, etc.)
8. **Acronym Control**: Can disable acronym expansion independently

### Test Status

- **149 total tests**: 45 comprehensive + 26 missing coverage + 16 entity extraction + 19 pronunciation mappings + 43 other
- **All tests passing**: 100% pass rate
- **Coverage**: ~66% overall goal: 80%+
