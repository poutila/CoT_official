"""Data models for the chunker module."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ChunkType(str, Enum):
    """Types of chunks that can be created."""

    TEXT = "text"  # Plain text content
    CODE = "code"  # Code block
    MIXED = "mixed"  # Contains both text and code
    SECTION_HEADER = "section_header"  # Section heading
    REQUIREMENT = "requirement"  # Requirement text
    CHECKLIST = "checklist"  # Checklist items
    TABLE = "table"  # Table content


class ChunkMetadata(BaseModel):
    """Metadata associated with a chunk."""

    source_file: str = Field(..., description="Source file path")
    section: str | None = Field(None, description="Section slug where chunk appears")
    subsection: str | None = Field(None, description="Subsection if applicable")

    # Code-related metadata
    has_code: bool = Field(False, description="Whether chunk contains code")
    code_languages: list[str] = Field(
        default_factory=list, description="Programming languages in chunk"
    )
    example_types: list[str] = Field(
        default_factory=list, description="Types of examples (good/bad/neutral)"
    )

    # Position information
    start_line: int | None = Field(None, description="Starting line in source")
    end_line: int | None = Field(None, description="Ending line in source")
    chunk_index: int = Field(..., description="Index of chunk in document")
    total_chunks: int = Field(..., description="Total chunks in document")

    # Semantic information
    topics: list[str] = Field(default_factory=list, description="Topics covered in chunk")
    keywords: list[str] = Field(default_factory=list, description="Important keywords")

    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.now, description="When chunk was created")
    processing_version: str = Field("0.1.0", description="Version of chunker used")


class Chunk(BaseModel):
    """A single chunk of content for embedding and retrieval."""

    # Core content
    chunk_id: str = Field(..., description="Unique identifier for chunk")
    content: str = Field(..., description="The actual text content")
    chunk_type: ChunkType = Field(..., description="Type of chunk")

    # Token information
    token_count: int = Field(..., description="Number of tokens in content")
    encoding_model: str = Field("cl100k_base", description="Tokenizer model used")

    # Overlap for context preservation
    overlap_prev: str | None = Field(None, description="Overlapping text from previous chunk")
    overlap_next: str | None = Field(None, description="Overlapping text from next chunk")
    overlap_token_count: int = Field(0, description="Tokens in overlap sections")

    # Relationships
    prev_chunk_id: str | None = Field(None, description="ID of previous chunk")
    next_chunk_id: str | None = Field(None, description="ID of next chunk")
    parent_chunk_id: str | None = Field(None, description="ID of parent chunk if hierarchical")

    # Metadata
    metadata: ChunkMetadata = Field(..., description="Associated metadata")

    # Computed properties
    @property
    def total_tokens(self) -> int:
        """Total tokens including overlaps."""
        return self.token_count + self.overlap_token_count

    @property
    def is_code_chunk(self) -> bool:
        """Check if this is primarily a code chunk."""
        return self.chunk_type == ChunkType.CODE or self.metadata.has_code

    @property
    def has_good_example(self) -> bool:
        """Check if chunk contains good examples."""
        return "good" in self.metadata.example_types

    @property
    def has_bad_example(self) -> bool:
        """Check if chunk contains bad examples."""
        return "bad" in self.metadata.example_types

    def to_embedding_text(self) -> str:
        """Generate text for embedding with context."""
        parts = []

        # Add section context if available
        if self.metadata.section:
            parts.append(f"Section: {self.metadata.section}")

        # Add type context for code
        if self.is_code_chunk and self.metadata.code_languages:
            parts.append(f"Language: {', '.join(self.metadata.code_languages)}")

        # Add example type if relevant
        if self.metadata.example_types:
            parts.append(f"Example type: {', '.join(self.metadata.example_types)}")

        # Add main content
        parts.append(self.content)

        # Join with newlines
        return "\n\n".join(parts)

    def to_retrieval_text(self) -> str:
        """Generate text for display after retrieval."""
        parts = []

        # Add metadata header
        if self.metadata.section:
            parts.append(f"📍 Section: {self.metadata.section}")

        if self.is_code_chunk:
            lang = self.metadata.code_languages[0] if self.metadata.code_languages else ""
            parts.append(f"```{lang}")
            parts.append(self.content)
            parts.append("```")
        else:
            parts.append(self.content)

        # Add context if available
        if self.overlap_prev:
            parts.insert(0, f"[...{self.overlap_prev[-50:]}]")
        if self.overlap_next:
            parts.append(f"[{self.overlap_next[:50]}...]")

        return "\n".join(parts)


class ChunkingConfig(BaseModel):
    """Configuration for chunking strategy."""

    max_tokens: int = Field(512, description="Maximum tokens per chunk")
    overlap_tokens: int = Field(50, description="Number of overlapping tokens")
    preserve_code_blocks: bool = Field(True, description="Never split code blocks")
    preserve_sections: bool = Field(False, description="Try to keep sections together")
    min_chunk_tokens: int = Field(50, description="Minimum tokens for a chunk")
    encoding_model: str = Field("cl100k_base", description="Tiktoken encoding model")

    # Strategy-specific settings
    respect_sentence_boundaries: bool = Field(True, description="Split at sentence boundaries")
    respect_paragraph_boundaries: bool = Field(True, description="Prefer paragraph boundaries")
    include_metadata_in_chunk: bool = Field(True, description="Include metadata in chunk content")

    def validate_config(self) -> bool:
        """Validate configuration settings."""
        if self.overlap_tokens >= self.max_tokens:
            raise ValueError("Overlap tokens must be less than max tokens")
        if self.min_chunk_tokens > self.max_tokens:
            raise ValueError("Min chunk tokens must be less than max tokens")
        return True
