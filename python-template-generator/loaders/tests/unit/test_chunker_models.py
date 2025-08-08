"""Unit tests for chunker models."""

import pytest
from chunker.models import Chunk, ChunkingConfig, ChunkMetadata, ChunkType
from pydantic import ValidationError


class TestChunkType:
    """Test ChunkType enum."""

    def test_chunk_types(self):
        """Test all chunk types are defined."""
        assert ChunkType.TEXT.value == "text"
        assert ChunkType.CODE.value == "code"
        assert ChunkType.MIXED.value == "mixed"
        assert ChunkType.SECTION_HEADER.value == "section_header"
        assert ChunkType.REQUIREMENT.value == "requirement"
        assert ChunkType.CHECKLIST.value == "checklist"
        assert ChunkType.TABLE.value == "table"


class TestChunkMetadata:
    """Test ChunkMetadata model."""

    def test_metadata_creation(self):
        """Test metadata creation with required fields."""
        meta = ChunkMetadata(source_file="test.md", chunk_index=0, total_chunks=1)
        assert meta.source_file == "test.md"
        assert meta.chunk_index == 0
        assert meta.total_chunks == 1
        assert meta.section is None
        assert meta.has_code is False
        assert meta.code_languages == []

    def test_metadata_with_values(self):
        """Test metadata with custom values."""
        meta = ChunkMetadata(
            source_file="doc.md",
            chunk_index=5,
            total_chunks=10,
            section="introduction",
            has_code=True,
            code_languages=["python", "bash"],
            start_line=100,
            end_line=150,
        )
        assert meta.source_file == "doc.md"
        assert meta.chunk_index == 5
        assert meta.total_chunks == 10
        assert meta.section == "introduction"
        assert meta.has_code is True
        assert meta.code_languages == ["python", "bash"]


class TestChunk:
    """Test Chunk model."""

    def test_chunk_creation(self):
        """Test basic chunk creation."""
        metadata = ChunkMetadata(source_file="test.md", chunk_index=0, total_chunks=1)
        chunk = Chunk(
            content="Test content",
            chunk_id="chunk-001",
            chunk_type=ChunkType.TEXT,
            token_count=10,
            metadata=metadata,
        )
        assert chunk.content == "Test content"
        assert chunk.chunk_id == "chunk-001"
        assert chunk.chunk_type == ChunkType.TEXT
        assert chunk.token_count == 10
        assert chunk.metadata.source_file == "test.md"

    def test_chunk_properties(self):
        """Test chunk computed properties."""
        metadata = ChunkMetadata(
            source_file="test.md",
            chunk_index=0,
            total_chunks=1,
            has_code=True,
            code_languages=["python"],
        )
        chunk = Chunk(
            content="def test(): pass",
            chunk_id="chunk-001",
            chunk_type=ChunkType.CODE,
            token_count=10,
            overlap_token_count=5,
            metadata=metadata,
        )
        assert chunk.total_tokens == 15  # token_count + overlap_token_count
        assert chunk.is_code_chunk is True

    def test_chunk_validation(self):
        """Test chunk validation."""
        # Missing required metadata fields should raise error
        with pytest.raises(ValidationError):
            metadata = ChunkMetadata()  # Missing required fields
            Chunk(
                content="Test",
                chunk_id="001",
                chunk_type=ChunkType.TEXT,
                token_count=1,
                metadata=metadata,
            )


class TestChunkingConfig:
    """Test ChunkingConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ChunkingConfig()
        assert config.max_tokens == 512
        assert config.overlap_tokens == 50
        assert config.min_chunk_tokens == 50
        assert config.respect_sentence_boundaries is True
        assert config.respect_paragraph_boundaries is True
        assert config.preserve_code_blocks is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = ChunkingConfig(
            max_tokens=1000,
            overlap_tokens=100,
            min_chunk_tokens=25,
            respect_sentence_boundaries=False,
        )
        assert config.max_tokens == 1000
        assert config.overlap_tokens == 100
        assert config.min_chunk_tokens == 25
        assert config.respect_sentence_boundaries is False

    def test_config_validation(self):
        """Test configuration validation."""
        # Test validate_config method
        config = ChunkingConfig(max_tokens=100, overlap_tokens=50)
        assert config.validate_config() is True

        # Overlap greater than max_tokens should fail
        config_invalid = ChunkingConfig(max_tokens=100, overlap_tokens=150)
        with pytest.raises(ValueError, match="Overlap tokens must be less than max tokens"):
            config_invalid.validate_config()

        # Min chunk greater than max should fail
        config_invalid2 = ChunkingConfig(max_tokens=100, min_chunk_tokens=150)
        with pytest.raises(ValueError, match="Min chunk tokens must be less than max tokens"):
            config_invalid2.validate_config()

    def test_config_validation_overlap(self):
        """Test that overlap is validated against max_tokens."""
        config = ChunkingConfig(max_tokens=100, overlap_tokens=50)
        assert config.overlap_tokens == 50

        # Test validation in validator
        config = ChunkingConfig(max_tokens=100)
        # This should pass validation
        assert config.overlap_tokens <= config.max_tokens
