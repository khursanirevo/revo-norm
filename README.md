# Revo Norm

**Text normalization library for TTS applications — English and Malay.**

> Designed for **text-to-speech** only. NOT for ASR preprocessing.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Install

```bash
pip install revo-norm
```

## Usage

```python
from revo_norm import normalize_text

# English
normalize_text("Meeting at 3:30 pm", language="en")

# Malay
normalize_text("Harga RM100 untuk 5 unit", language="ms")

# With profile
normalize_text(text, language="en", profile="basic")

# Disable features
normalize_text(text, language="en", disable=["temperature", "measurements"])
```

## Documentation

**[khursanirevo.github.io/revo-norm](https://khursanirevo.github.io/revo-norm/)**

## License

MIT
