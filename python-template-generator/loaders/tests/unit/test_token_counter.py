"""Unit tests for token counter."""

from unittest.mock import patch

import pytest
from chunker.token_counter import TokenCounter


class TestTokenCounter:
    """Test TokenCounter class."""

    def test_initialization_default(self):
        """Test default initialization."""
        counter = TokenCounter()
        assert counter.encoding_model == "cl100k_base"
        assert counter.encoder is not None

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        counter = TokenCounter(encoding_model="p50k_base")
        assert counter.encoding_model == "p50k_base"

    def test_count_tokens_empty(self):
        """Test counting tokens in empty string."""
        counter = TokenCounter()
        assert counter.count("") == 0

    def test_count_tokens_simple(self):
        """Test counting tokens in simple text."""
        counter = TokenCounter()
        text = "Hello world"
        count = counter.count(text)
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_complex(self):
        """Test counting tokens in complex text."""
        counter = TokenCounter()
        text = """This is a more complex text with multiple sentences.
        It includes punctuation, numbers like 123, and special characters!
        Let's see how many tokens this generates."""
        count = counter.count(text)
        assert count > 10  # Should have multiple tokens

    def test_encode_decode(self):
        """Test encoding and decoding text."""
        counter = TokenCounter()
        text = "Test encoding and decoding"

        tokens = counter.encode(text)
        assert isinstance(tokens, list)
        assert len(tokens) > 0

        decoded = counter.decode(tokens)
        assert decoded == text

    def test_split_at_token_limit_simple(self):
        """Test splitting text at token limit."""
        counter = TokenCounter()
        text = "This is a test. " * 20  # Repeat to ensure we exceed limit

        chunks = counter.split_at_token_limit(text, max_tokens=10, overlap_tokens=2)

        assert len(chunks) > 1
        for chunk in chunks:
            tokens = counter.count(chunk)
            assert tokens <= 12  # Allow for overlap

    def test_split_at_token_limit_no_overlap(self):
        """Test splitting without overlap."""
        counter = TokenCounter()
        text = "Word " * 50

        chunks = counter.split_at_token_limit(text, max_tokens=10, overlap_tokens=0)

        # Just verify we get multiple chunks
        assert len(chunks) > 1

    def test_split_at_token_limit_with_overlap(self):
        """Test splitting with overlap."""
        counter = TokenCounter()
        text = " ".join([f"word{i}" for i in range(100)])

        chunks = counter.split_at_token_limit(text, max_tokens=20, overlap_tokens=5)

        assert len(chunks) > 1
        # Each chunk should be within reasonable limit (accounting for overlap)
        for chunk in chunks:
            assert counter.count(chunk) <= 25

    def test_find_optimal_split(self):
        """Test finding optimal split point."""
        counter = TokenCounter()
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."

        # Test the find_optimal_split_point method
        split_point = counter.find_optimal_split_point(text, target_tokens=10)

        # Should find a split point somewhere in the text
        assert 0 < split_point <= len(text)

    def test_split_empty_text(self):
        """Test splitting empty text."""
        counter = TokenCounter()
        chunks = counter.split_at_token_limit("", max_tokens=10)
        assert chunks == [""]  # tiktoken returns empty string for empty input

    def test_split_text_shorter_than_limit(self):
        """Test splitting text shorter than limit."""
        counter = TokenCounter()
        text = "Short text"
        chunks = counter.split_at_token_limit(text, max_tokens=100)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_encode_decode(self):
        """Test encoding and decoding."""
        counter = TokenCounter()
        text = "Hello world"
        tokens = counter.encode(text)

        assert isinstance(tokens, list)
        assert len(tokens) > 0

        # Test decode
        decoded = counter.decode(tokens)
        assert decoded == text

    def test_estimate_chunks_needed(self):
        """Test estimating chunks needed."""
        counter = TokenCounter()
        text = "This is a long text " * 50

        estimate = counter.estimate_chunks_needed(text, max_tokens=10)
        assert estimate > 0
        assert isinstance(estimate, int)

    def test_estimate_tokens(self):
        """Test static token estimation without encoding."""
        text = "This is a test of token estimation"

        # Static method doesn't need instance
        estimated = TokenCounter.estimate_tokens(text)

        # Should give reasonable estimate
        assert estimated > 0
        assert isinstance(estimated, int)

    def test_overlap_validation(self):
        """Test that overlap is properly validated."""
        counter = TokenCounter()
        text = "Test " * 20

        # Overlap >= max_tokens should be adjusted
        chunks = counter.split_at_token_limit(
            text,
            max_tokens=10,
            overlap_tokens=15,  # Greater than max
        )

        # Should still produce valid chunks
        assert len(chunks) > 0
        # Chunks should not be too large even with overlap
        for chunk in chunks:
            # Allow some flexibility for overlap handling
            assert counter.count(chunk) <= 20

    @patch("tiktoken.get_encoding")
    def test_encoding_error_handling(self, mock_get_encoding):
        """Test handling of encoding errors."""
        mock_get_encoding.side_effect = Exception("Encoding error")

        with pytest.raises(Exception) as exc_info:
            TokenCounter()
        assert "Encoding error" in str(exc_info.value)
