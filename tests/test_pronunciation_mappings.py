"""
Tests for pronunciation mappings system.

This test suite verifies that pronunciation mappings are applied correctly
and prevent unwanted transformations (e.g., "JSON" → "jay son", not "J S O N").
"""

import pytest

try:
    from revo_norm import normalize_text
    from revo_norm.pronunciation_mappings import (
        apply_pronunciation_mappings,
        add_custom_mapping,
        get_pronunciation_mappings,
        remove_preservation_markers,
    )

    PRONUNCIATION_AVAILABLE = True
except ImportError:
    PRONUNCIATION_AVAILABLE = False


@pytest.mark.skipif(
    not PRONUNCIATION_AVAILABLE, reason="Pronunciation mappings not available"
)
class TestPronunciationMappings:
    """Test pronunciation mapping functionality."""

    def test_json_pronunciation(self):
        """Test JSON is pronounced as 'jay son' not 'J S O N'."""
        text = "Parse JSON file"
        result = normalize_text(text, language="en")

        assert "jay son" in result
        assert "J S O N" not in result
        assert "JAY SON" not in result

    def test_gui_pronunciation(self):
        """Test GUI is pronounced as 'gooey' not 'G U I'."""
        text = "Build GUI interface"
        result = normalize_text(text, language="en")

        assert "gooey" in result
        assert "G U I" not in result

    def test_ml_preserved(self):
        """Test ML is preserved (not split into 'M L')."""
        text = "Train ML model"
        result = normalize_text(text, language="en")

        assert "ML" in result
        assert "M L" not in result

    def test_ai_preserved(self):
        """Test AI is preserved (not split into 'A I')."""
        text = "AI and ML model"
        result = normalize_text(text, language="en")

        assert "AI" in result
        assert "A I" not in result

    def test_llm_preserved(self):
        """Test LLM is preserved (not split into 'L L M')."""
        text = "Train LLM for NLP"
        result = normalize_text(text, language="en")

        assert "LLM" in result
        assert "L L M" not in result

    def test_api_preserved(self):
        """Test API is preserved (not split into 'A P I')."""
        text = "RESTful API endpoint"
        result = normalize_text(text, language="en")

        assert "API" in result
        assert "A P I" not in result

    def test_json_api_combined(self):
        """Test JSON and API in same sentence."""
        text = "JSON API response"
        result = normalize_text(text, language="en")

        assert "jay son" in result
        assert "API" in result
        assert "A P I" not in result

    def test_http_pronunciation(self):
        """Test HTTP is pronounced as 'H T T P'."""
        text = "HTTP and HTTPS"
        result = normalize_text(text, language="en")

        assert "H T T P" in result
        assert "H T T P S" in result

    def test_tech_stack_preserved(self):
        """Test multiple tech acronyms are preserved."""
        text = "Use GPU and CPU with NLP"
        result = normalize_text(text, language="en")

        assert "GPU" in result
        assert "CPU" in result
        assert "NLP" in result

    def test_pandas_numpy_preserved(self):
        """Test library names are preserved."""
        text = "Use pandas and numpy"
        result = normalize_text(text, language="en")

        assert "pandas" in result
        assert "numpy" in result


@pytest.mark.skipif(
    not PRONUNCIATION_AVAILABLE, reason="Pronunciation mappings not available"
)
class TestPronunciationMappingsMalay:
    """Test pronunciation mappings for Malay language."""

    def test_json_malay(self):
        """Test JSON pronunciation in Malay."""
        text = "Fail JSON"
        result = normalize_text(text, language="ms")

        assert "jay son" in result

    def test_ml_malay(self):
        """Test ML is preserved in Malay."""
        text = "Latih model ML"
        result = normalize_text(text, language="ms")

        assert "ML" in result
        assert "M L" not in result


@pytest.mark.skipif(
    not PRONUNCIATION_AVAILABLE, reason="Pronunciation mappings not available"
)
class TestPronunciationMappingsAPI:
    """Test pronunciation mapping API functions."""

    def test_get_pronunciation_mappings_en(self):
        """Test getting English pronunciation mappings."""
        mappings = get_pronunciation_mappings("en")

        assert "JSON" in mappings
        assert mappings["JSON"] == "jay son"
        assert "GUI" in mappings
        assert mappings["GUI"] == "gooey"

    def test_get_pronunciation_mappings_ms(self):
        """Test getting Malay pronunciation mappings."""
        mappings = get_pronunciation_mappings("ms")

        assert "JSON" in mappings
        assert mappings["JSON"] == "jay son"

    def test_add_custom_mapping(self):
        """Test adding a custom pronunciation mapping."""
        # Add custom mapping
        add_custom_mapping("YOLO", "you only live once", "en")

        # Verify it's in the mappings
        mappings = get_pronunciation_mappings("en")
        assert "YOLO" in mappings
        assert mappings["YOLO"] == "you only live once"

    def test_apply_pronunciation_mappings_direct(self):
        """Test applying pronunciation mappings directly."""
        text = "Parse JSON file"
        result = apply_pronunciation_mappings(text, "en")

        assert "jay son" in result
        assert "JSON" not in result

    def test_remove_preservation_markers(self):
        """Test removing preservation markers."""
        text = "Train __PRESERVED__ML__ model"
        result = remove_preservation_markers(text)

        assert result == "Train ML model"
        assert "__PRESERVED__" not in result


@pytest.mark.skipif(
    not PRONUNCIATION_AVAILABLE, reason="Pronunciation mappings not available"
)
class TestPronunciationMappingsIntegration:
    """Test pronunciation mappings with full pipeline."""

    def test_complex_sentence(self):
        """Test complex sentence with multiple mapped terms."""
        text = "Build RESTful API using JSON for ML and AI models"
        result = normalize_text(text, language="en")

        # JSON should be pronounced
        assert "jay son" in result

        # API, ML, AI should be preserved
        assert "API" in result
        assert "ML" in result
        assert "AI" in result

        # Should NOT be split
        assert "A P I" not in result
        assert "M L" not in result
        assert "A I" not in result

    def test_pronunciation_before_acronym_expansion(self):
        """Test that pronunciation mappings happen before acronym expansion."""
        # This verifies the order: mappings → acronym expansion

        # "JSON" is mapped to "jay son" (pronunciation)
        # "API" is mapped to itself (preserved from acronym splitting)
        # "ML" is mapped to itself (preserved from acronym splitting)
        text = "JSON API ML"
        result = normalize_text(text, language="en")

        # Pronunciation mapping applied
        assert "jay son" in result

        # Acronym expansion skipped for preserved terms
        assert "API" in result
        assert "ML" in result
        assert "A P I" not in result
        assert "M L" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
