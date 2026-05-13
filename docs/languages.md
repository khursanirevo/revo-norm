# Language Support

Revo-norm supports two languages with awareness of code-mixing patterns common in Southeast Asian contexts.

## Supported Languages

| Code | Language | Notes |
|------|----------|-------|
| `en` | English | Full normalization with contractions, ordinals, abbreviations |
| `ms` | Malay (Bahasa Melayu) | Full normalization with Malay number words, currency, local features |

```python
from revo_norm import normalize_text

result_en = normalize_text("25C outside", language="en")
# "twenty five degrees celsius outside"

result_ms = normalize_text("25C di luar", language="ms")
# "dua puluh lima darjah selsius di luar"
```

---

## Code-Mixing

Malaysian Malay text frequently mixes in English terms. Revo-norm handles this naturally -- the language parameter controls which normalizer runs on the non-entity text, but English technical terms (API, ML, GPU, etc.) are handled consistently regardless of language.

```python
# English terms in a Malay sentence
result = normalize_text("Projek ML ni guna 5GB RAM", language="ms")
# "Projek M L ni guna lima gigabyte R A M"

# Malay terms in an English sentence
result = normalize_text("The ringgit fell 5% today", language="en")
# "The ringgit fell five percent today"
```

Pronunciation mappings apply to both languages equally -- terms like `GUI`, `ASCII`, and `IEEE` are mapped to their spoken forms regardless of the `language` parameter.

---

## English Specifics (`language="en"`)

### Contractions

Common English contractions are expanded to their full forms for clean TTS output:

```python
normalize_text("I'm happy they can't come", language="en")
# "I am happy they cannot come"
```

Supported contractions include:
- **Pronoun + verb:** `I'm` -> `I am`, `you're` -> `you are`, `it's` -> `it is`
- **Negations:** `don't` -> `do not`, `can't` -> `cannot`, `won't` -> `will not`
- **Perfect tense:** `should've` -> `should have`, `could've` -> `could have`
- **Question words:** `what's` -> `what is`, `where's` -> `where is`

Over 60 contractions are handled, including negative forms, possessive-like forms, and perfect tense contractions.

### Ordinals

English ordinal numbers are converted to their spoken form:

```python
normalize_text("She finished 1st in the 21st century", language="en")
# "She finished first in the twenty first century"
```

### Abbreviations

Common title and place abbreviations are expanded:

| Abbreviation | Spoken Form |
|-------------|-------------|
| `Mr.` | `Mister` |
| `Mrs.` | `Misess` |
| `Dr.` | `Doctor` |
| `St.` | `Saint` |
| `Jr.` | `Junior` |
| `Ltd.` | `Limited` |
| `Capt.` | `Captain` |
| `Gen.` | `General` |
| `Sgt.` | `Sergeant` |

### Numbers and Currency

```python
normalize_text("1,000,000 dollars at 3.5%", language="en")
# "one million dollars at three point five percent"

normalize_text("The price is $45.99", language="en")
# "The price is forty five dollar ninety nine cent"
```

### Years

Four-digit numbers in the 1000-2099 range are read as years:

```python
normalize_text("Born in 1990, graduated 2012", language="en")
# "Born in nineteen ninety, graduated twenty twelve"
```

### Dates and Times

```python
normalize_text("Meeting on 15/08/2025 at 3:30 pm", language="en")
# "Meeting on fifteenth of August, two thousand and twenty five at three thirty p m"
```

---

## Malay Specifics (`language="ms"`)

### Number Words

Numbers are converted to Malay number words:

| Number | Malay |
|--------|-------|
| 0 | kosong |
| 1 | satu |
| 10 | sepuluh |
| 11 | sebelas |
| 42 | empat puluh dua |
| 100 | seratus |
| 1000 | seribu |
| 1,000,000 | satu juta |

The special contracted forms are used automatically:
- `sebelas` (eleven, not `satu belas`)
- `sepuluh` (ten, but the combined form in compounds)
- `seratus` (one hundred, not `satu ratus`)
- `seribu` (one thousand, not `satu ribu`)

```python
normalize_text("Ada 115 orang", language="ms")
# "Ada seratus lima belas orang"
```

### Currency

Ringgit Malaysia (RM) is the primary currency, with `ringgit` as the main unit and `sen` as the subunit:

```python
normalize_text("Harga RM 450.50", language="ms")
# "Harga empat ratus lima puluh ringgit lima puluh sen"

normalize_text("RM30K untuk projek ni", language="ms")
# "tiga puluh ribu ringgit untuk projek ni"
```

Supported currency symbols: `RM`, `$`, `£`, `EUR`, `USD`, `GBP`, `MYR`. Amount suffixes `K`, `M`, `B`, `T` are expanded to full numbers.

### Date Months

Malay month names are used when normalizing dates:

| Month | Malay |
|-------|-------|
| January | Januari |
| February | Februari |
| March | Mac |
| April | April |
| May | Mei |
| June | Jun |
| July | Julai |
| August | Ogos |
| September | September |
| October | Oktober |
| November | November |
| December | Disember |

```python
normalize_text("Tarikh: 15/08/2025", language="ms")
# "Tarikh: lima belas Ogos dua ribu dua puluh lima"
```

### Time Meridians

Malay time expressions use `pagi` (morning/AM) and `petang` (afternoon/PM):

```python
normalize_text("Jumpa pukul 8:30 pagi", language="ms")
# "Jumpa pukul lapan tiga puluh pagi"
```

### Malaysian Identity Card Numbers (IC)

Malaysian IC numbers (12 digits in `YYMMDD-SS-XXXX` format) are normalized to spoken form:

```python
normalize_text("No IC: 901231-10-5678", language="ms")
# The IC number is expanded digit by digit with structural grouping
```

### Elongated Words

Common in informal Malay text, repeated characters are reduced:

```python
normalize_text("Sedihhh sangat laa", language="ms")
# "Sedih sangat la"
```

### Measurements

Unit abbreviations are expanded to their spoken Malay forms:

```python
normalize_text("Berat 5kg, jarak 10km", language="ms")
# "Berat lima kilogram, jarak sepuluh kilometer"
```

### Decimals and Percentages

```python
normalize_text("Kadar 3.5% setahun", language="ms")
# "Kadar tiga perpuluhan lima peratus setahun"
```

### Hijri Calendar

Islamic/Hijri year conversion is supported:

```python
normalize_text("Tahun Hijri 1446", language="ms")
# Hijri year converted to spoken form
```

---

## Common Gotchas

### DD/MM vs MM/DD Date Ambiguity

The library assumes **DD/MM/YYYY** format (common in Malaysia and most of the world), not MM/DD/YYYY (US format). This is a heuristic-based approach and ambiguous dates where both day and month are 12 or less may be parsed incorrectly.

```python
# Unambiguous: day > 12
normalize_text("15/08/2025", language="en")
# "fifteenth of August, two thousand and twenty five" (correct)

# Ambiguous: both <= 12
normalize_text("05/06/2025", language="en")
# Treated as 5th of June (DD/MM), not June 5th (MM/DD)
```

If your source text uses US date format (MM/DD/YYYY), consider pre-processing dates before passing them to revo-norm.

### "RM" in Currency vs Other Meanings

`RM` is recognized as Ringgit Malaysia in currency contexts. In non-currency contexts, it may be treated differently:

```python
# Currency context -- handled correctly
normalize_text("Harga RM 450", language="ms")
# "Harga empat ratus lima puluh ringgit"

# As part of a word or acronym -- protected by pronunciation mappings
normalize_text("The RM team", language="en")
# "The R M team" (split as acronym)
```

### All-Caps Tech Terms (AI, ML, LLM)

All-caps tech terms like `AI`, `ML`, `LLM`, `GPU`, `API` are handled by the pronunciation mappings and acronym expansion systems. The pipeline applies pronunciation mappings first (highest priority), then acronym expansion:

```python
# AI, ML, LLM -- split letter by letter by expand_acronym()
normalize_text("Train ML models with AI", language="en")
# "Train M L models with A I"

# GUI -- mapped to "gooey" by pronunciation mappings (applied first)
normalize_text("Build a GUI app", language="en")
# "Build a gooey app"

# Custom pronunciation
from revo_norm.pronunciation_mappings import add_custom_mapping
add_custom_mapping("YOLO", "you only live once", "en")
normalize_text("YOLO approach", language="en")
# "you only live once approach"
```

### Entity Extraction Protects Patterns

The entity extraction system runs early in the pipeline and protects recognized patterns from being mangled by downstream transformations. This prevents issues like:

- `RM 450` being split into `R M 450` by acronym expansion (currency is extracted as an entity first)
- Dates like `15/08/2025` being interpreted as fractions
- URLs containing numbers from being partially converted

If a specific entity type is causing issues, you can disable it:

```python
normalize_text(text, language="ms", disable=["fractions"])
```
