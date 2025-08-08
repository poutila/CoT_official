"""Base abstract chunker class defining the interface."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Protocol
from pathlib import Path
import hashlib
import uuid

from .models import Chunk, ChunkMetadata, ChunkType, ChunkingConfig
from .token_counter import TokenCounter


class Document(Protocol):
    """Protocol for documents that can be chunked.
    
    Any document that has sections and can be converted to text
    can be chunked by implementing this protocol.
    """
    @property
    def sections(self) -> List[Any]:
        """Get document sections."""
        ...
    
    def to_text(self) -> str:
        """Convert document to plain text."""
        ...


class BaseChunker(ABC):
    """Abstract base class for all chunking strategies."""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize chunker with configuration.
        
        Args:
            config: Chunking configuration, uses defaults if not provided
        """
        self.config = config or ChunkingConfig()
        self.config.validate_config()
        self.token_counter = TokenCounter(self.config.encoding_model)
        self._chunk_cache = {}
    
    @abstractmethod
    def chunk(self, document: Any, **kwargs) -> List[Chunk]:
        """Chunk a document into smaller pieces.
        
        Args:
            document: Document to chunk (specific type depends on implementation)
            **kwargs: Additional strategy-specific parameters
            
        Returns:
            List of chunks
        """
        pass
    
    def chunk_text(self, text: str, source_file: str = "unknown", **kwargs) -> List[Chunk]:
        """Chunk plain text into smaller pieces.
        
        This is a convenience method for chunking plain text without
        a full document structure.
        
        Args:
            text: Plain text to chunk
            source_file: Source file name for metadata
            **kwargs: Additional parameters
            
        Returns:
            List of chunks
        """
        # Default implementation - can be overridden
        chunks = self._simple_text_chunking(text, source_file)
        return self._add_chunk_relationships(chunks)
    
    def _simple_text_chunking(self, text: str, source_file: str) -> List[Chunk]:
        """Simple text chunking by token count.
        
        Args:
            text: Text to chunk
            source_file: Source file for metadata
            
        Returns:
            List of chunks
        """
        chunks = []
        
        # Split text at token boundaries
        text_pieces = self.token_counter.split_at_token_limit(
            text,
            self.config.max_tokens,
            self.config.overlap_tokens
        )
        
        for i, piece in enumerate(text_pieces):
            chunk_id = self._generate_chunk_id(piece, i)
            
            # Create metadata
            metadata = ChunkMetadata(
                source_file=source_file,
                chunk_index=i,
                total_chunks=len(text_pieces),
                has_code=self._detect_code(piece)
            )
            
            # Create chunk
            chunk = Chunk(
                chunk_id=chunk_id,
                content=piece,
                chunk_type=self._detect_chunk_type(piece),
                token_count=self.token_counter.count(piece),
                encoding_model=self.config.encoding_model,
                metadata=metadata
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def _add_chunk_relationships(self, chunks: List[Chunk]) -> List[Chunk]:
        """Add relationships between chunks (prev/next IDs and overlaps).
        
        Args:
            chunks: List of chunks to add relationships to
            
        Returns:
            Chunks with relationships added
        """
        for i, chunk in enumerate(chunks):
            # Add previous chunk reference
            if i > 0:
                chunk.prev_chunk_id = chunks[i - 1].chunk_id
                
                # Add overlap if configured
                if self.config.overlap_tokens > 0:
                    # Extract overlap from previous chunk
                    prev_content = chunks[i - 1].content
                    overlap_tokens = min(
                        self.config.overlap_tokens,
                        self.token_counter.count(prev_content)
                    )
                    
                    # Get last N tokens from previous chunk
                    prev_tokens = self.token_counter.encode(prev_content)
                    if len(prev_tokens) > overlap_tokens:
                        overlap_text = self.token_counter.decode(
                            prev_tokens[-overlap_tokens:]
                        )
                        chunk.overlap_prev = overlap_text
            
            # Add next chunk reference
            if i < len(chunks) - 1:
                chunk.next_chunk_id = chunks[i + 1].chunk_id
                
                # Add overlap if configured
                if self.config.overlap_tokens > 0:
                    # Extract overlap from next chunk
                    next_content = chunks[i + 1].content
                    overlap_tokens = min(
                        self.config.overlap_tokens,
                        self.token_counter.count(next_content)
                    )
                    
                    # Get first N tokens from next chunk
                    next_tokens = self.token_counter.encode(next_content)
                    if len(next_tokens) > overlap_tokens:
                        overlap_text = self.token_counter.decode(
                            next_tokens[:overlap_tokens]
                        )
                        chunk.overlap_next = overlap_text
            
            # Update overlap token count
            chunk.overlap_token_count = (
                self.token_counter.count(chunk.overlap_prev or "") +
                self.token_counter.count(chunk.overlap_next or "")
            )
        
        return chunks
    
    def _generate_chunk_id(self, content: str, index: int) -> str:
        """Generate unique ID for a chunk.
        
        Args:
            content: Chunk content
            index: Chunk index in document
            
        Returns:
            Unique chunk ID
        """
        # Create ID from content hash and index
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"chunk_{index:04d}_{content_hash}"
    
    def _detect_chunk_type(self, text: str) -> ChunkType:
        """Detect the type of content in a chunk.
        
        Args:
            text: Chunk text
            
        Returns:
            Detected chunk type
        """
        # Simple heuristics - can be overridden for more sophisticated detection
        
        # Check for code blocks
        if "```" in text or self._detect_code(text):
            # Check if it's mixed content
            if len(text.split("```")[0].strip()) > 100:
                return ChunkType.MIXED
            return ChunkType.CODE
        
        # Check for headers
        if text.strip().startswith("#"):
            return ChunkType.SECTION_HEADER
        
        # Check for requirements patterns
        if any(marker in text.upper() for marker in ["MUST", "SHALL", "SHOULD", "REQUIRED"]):
            return ChunkType.REQUIREMENT
        
        # Check for checklist
        if "- [ ]" in text or "- [x]" in text or "- [X]" in text:
            return ChunkType.CHECKLIST
        
        # Check for table
        if "|" in text and "-|-" in text:
            return ChunkType.TABLE
        
        # Default to text
        return ChunkType.TEXT
    
    def _detect_code(self, text: str) -> bool:
        """Detect if text contains code.
        
        Args:
            text: Text to check
            
        Returns:
            True if code is detected
        """
        code_indicators = [
            "```",
            "def ",
            "class ",
            "import ",
            "from ",
            "function ",
            "const ",
            "let ",
            "var ",
            "return ",
            "if __name__",
            "async def",
            "await ",
        ]
        
        return any(indicator in text for indicator in code_indicators)
    
    def estimate_chunks(self, document: Any) -> int:
        """Estimate number of chunks that will be created.
        
        Args:
            document: Document to estimate for
            
        Returns:
            Estimated number of chunks
        """
        # Get text representation
        if hasattr(document, 'to_text'):
            text = document.to_text()
        else:
            text = str(document)
        
        return self.token_counter.estimate_chunks_needed(
            text,
            self.config.max_tokens,
            self.config.overlap_tokens
        )
    
    def clear_cache(self):
        """Clear internal caches."""
        self._chunk_cache.clear()
        self.token_counter.clear_cache()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get chunker statistics."""
        return {
            "config": self.config.model_dump(),
            "cache_size": len(self._chunk_cache),
            "token_cache_size": self.token_counter.cache_size,
        }