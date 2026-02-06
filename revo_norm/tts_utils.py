"""
TTS-specific utility functions for the ChatterBox backend.

This module contains features specific to TTS processing that should NOT
be in the general text normalization library (revo-norm).

Features:
- Sentence splitting and chunking for TTS
- Random comma insertion for pauses
- Sound word removal (laughter, applause, etc.)
- Repetitive sequence detection
"""

import random
import re
from typing import List, Tuple


def normalize_problematic_chars(text: str) -> str:
    """
    Normalize problematic Unicode characters that confuse TTS models.
    - Em dashes to commas (for pauses)
    - Smart quotes to straight quotes
    - Excessive quote sequences
    """
    # Replace em dashes and en dashes with commas or spaces (for pauses)
    text = re.sub(r"[—–]", ", ", text)

    # Normalize all quote variations to straight single quotes
    text = text.replace('"', "'").replace('"', "'")
    text = text.replace(""", "'").replace(""", "'")
    text = text.replace("`", "'")  # Backtick to quote

    # Remove excessive quote sequences but keep single quotes for dialogue
    text = re.sub(r"'+", "'", text)
    text = re.sub(r'"+', '"', text)

    # Clean up any double spaces or commas
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r",\s*,", ",", text)

    return text.strip()


def parse_sound_word_field(user_input: str) -> List[Tuple[str, str]]:
    """Parse sound word field input into list of (pattern, replacement) tuples."""
    lines = [l.strip() for l in user_input.split("\n") if l.strip()]
    result = []
    for line in lines:
        if "=>" in line:
            pattern, replacement = line.split("=>", 1)
            result.append((pattern.strip(), replacement.strip()))
        else:
            result.append((line, ""))
    return result


def smart_remove_sound_words(text: str, sound_words: List[Tuple[str, str]]) -> str:
    """Remove or replace sound words like [laughter], [applause] from text."""
    for pattern, replacement in sound_words:
        if replacement:
            text = re.sub(
                r"(?i)(%s)([" "']s?)" % re.escape(pattern),
                lambda m: replacement + "'s" if m.group(2) else replacement,
                text,
            )
            text = re.sub(
                r'(["\'])%s(["\'])' % re.escape(pattern),
                lambda m: f"{m.group(1)}{replacement}{m.group(2)}",
                text,
                flags=re.IGNORECASE,
            )
            if all(char in "-——" for char in pattern.strip()):
                text = re.sub(re.escape(pattern), replacement, text)
            else:
                text = re.sub(
                    r"\b%s\b" % re.escape(pattern), replacement, text, flags=re.IGNORECASE
                )
        else:
            text = re.sub(r"%s" % re.escape(pattern), "", text, flags=re.IGNORECASE)

    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([,\s]+,)+", ",", text)
    text = re.sub(r",\s*,+", ",", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"(\s+,|,\s+)", ", ", text)
    text = re.sub(r"(^|[\.!\?]\s*),+", r"\1", text)
    text = re.sub(r",+\s*([\.!\?])", r"\1", text)
    return text.strip()


def split_repetitive_sequences(
    text: str, min_repeat_length: int = 1, repeat_threshold: int = 3
) -> List[str]:
    """Split text with repetitive sequences into separate segments."""
    original_words = text.split()
    clean_words = [re.sub(r"[^\w\s]", "", w).lower() for w in original_words]

    if len(clean_words) < min_repeat_length * repeat_threshold:
        return [text]

    segments = []
    current_segment_words = []

    i = 0
    while i < len(clean_words):
        found_repetition = False
        for length in range(min_repeat_length, (len(clean_words) - i) // repeat_threshold + 1):
            if i + length * repeat_threshold <= len(clean_words):
                pattern = clean_words[i : i + length]
                is_repetitive = True
                for k in range(1, repeat_threshold):
                    if clean_words[i + k * length : i + (k + 1) * length] != pattern:
                        is_repetitive = False
                        break

                if is_repetitive:
                    if current_segment_words:
                        segments.append(" ".join(current_segment_words))
                        current_segment_words = []

                    segments.append(
                        " ".join(original_words[i : i + length * repeat_threshold]) + "."
                    )
                    i += length * repeat_threshold
                    found_repetition = True
                    break

        if not found_repetition:
            current_segment_words.append(original_words[i])
            i += 1

    if current_segment_words:
        segments.append(" ".join(current_segment_words))

    return [s.strip() for s in segments if s.strip()]


def add_random_commas(text: str, min_words: int = 8, max_words: int = 15) -> str:
    """
    Add random commas for pauses in TTS output.

    Smarter logic:
    - Only add commas after many words (min_words=8, not 2-5)
    - Don't add comma if there's already punctuation within 2-3 words
    - Don't add comma if near end of sentence

    Args:
        text: Input text
        min_words: Minimum words before considering a comma (default=8)
        max_words: Maximum words before forcing a comma (default=15)
    """
    words = text.split()
    if len(words) < min_words:
        return text

    new_words = []
    word_count = 0
    last_punctuation_pos = -float("inf")  # Track position of last punctuation

    for i, word in enumerate(words):
        new_words.append(word)

        # Check if current word has sentence-ending punctuation
        ends_sentence = re.search(r"[.!?]$", word)
        has_comma = "," in word

        # Update last punctuation position
        if ends_sentence or has_comma:
            last_punctuation_pos = i

        # Only consider adding comma if:
        # 1. Not at end of sentence
        # 2. Not the last word
        # 3. Enough words have passed (min_words)
        # 4. No punctuation within 2-3 words ahead
        # 5. Random chance based on word count
        if not ends_sentence and not has_comma and i < len(words) - 1:
            word_count += 1

            if word_count >= min_words:
                # Check if there's punctuation coming up soon (within 2-3 words)
                upcoming_punctuation = False
                for j in range(i + 1, min(i + 4, len(words))):
                    if re.search(r"[.!?,:;]", words[j]):
                        upcoming_punctuation = True
                        break

                # Only add comma if:
                # - No punctuation coming up soon
                # - Random chance based on word count (longer text = higher chance)
                # - Not too close to end of sentence
                if not upcoming_punctuation and word_count <= max_words:
                    # Higher chance as word count increases
                    chance = word_count / max_words
                    if random.random() < chance:
                        new_words.append(",")
                        word_count = 0
                        last_punctuation_pos = i
                elif word_count >= max_words:
                    # Force comma if max words reached (but still check for upcoming punctuation)
                    if not upcoming_punctuation and i < len(words) - 3:
                        new_words.append(",")
                        word_count = 0
                        last_punctuation_pos = i
        elif ends_sentence or has_comma:
            word_count = 0
            last_punctuation_pos = i

    return " ".join(new_words).replace(" ,", ",")


def split_text_by_words(text: str, max_chars: int = 150) -> list[str]:
    """
    Split text into chunks by word boundaries (respects word integrity).

    This function ensures that words are never cut in half. It splits
    text into chunks that are approximately max_chars long, but will
    exceed this limit if necessary to avoid cutting a word.

    Args:
        text: Input text to split
        max_chars: Target maximum characters per chunk (default: 150)

    Returns:
        List of text chunks, each containing complete words

    Example:
        >>> split_text_by_words("the secret passage under the cottage", 20)
        ['the secret passage', 'under the cottage']
        >>> split_text_by_words("Di halaman rumah nenek", 10)
        ['Di halaman', 'rumah nenek']
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_len = len(word)

        # Check if adding this word would exceed max_chars
        # Only start a new chunk if we already have content
        if current_chunk and current_length + word_len + 1 > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(word)
        current_length += word_len + (1 if current_chunk else 0)

    # Add the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
