"""Semantic chunker that preserves code examples and respects document structure."""

from typing import List, Optional, Dict, Any, Tuple
import re
from pathlib import Path

from .base_chunker import BaseChunker
from .models import Chunk, ChunkMetadata, ChunkType, ChunkingConfig


class SemanticChunker(BaseChunker):
    """Intelligent chunker that preserves semantic boundaries.
    
    This chunker:
    - Never splits code examples
    - Respects section boundaries when possible
    - Maintains context through smart overlaps
    - Optimizes for embedding and retrieval quality
    """
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize semantic chunker.
        
        Args:
            config: Chunking configuration
        """
        super().__init__(config)
        
        # Ensure code preservation is enabled for semantic chunking
        if config:
            config.preserve_code_blocks = True
    
    def chunk(self, document: Any, **kwargs) -> List[Chunk]:
        """Chunk a document intelligently preserving semantic units.
        
        Args:
            document: Document to chunk (should have full_examples, sections, etc.)
            **kwargs: Additional parameters
            
        Returns:
            List of semantic chunks
        """
        # Handle different document types
        if hasattr(document, 'full_examples'):
            # This is our FullEnhancedDoc
            return self._chunk_enhanced_document(document)
        elif hasattr(document, 'sections'):
            # Generic document with sections
            return self._chunk_sectioned_document(document)
        else:
            # Fall back to text chunking
            text = str(document)
            source = kwargs.get('source_file', 'unknown')
            return self.chunk_text(text, source)
    
    def _chunk_enhanced_document(self, doc: Any) -> List[Chunk]:
        """Chunk an enhanced document with code examples.
        
        Args:
            doc: FullEnhancedDoc or similar with code examples
            
        Returns:
            List of chunks preserving code examples
        """
        chunks = []
        current_section = None
        current_text_buffer = []
        current_tokens = 0
        
        # Get source file from doc if available
        source_file = getattr(doc, 'source_file', 'document')
        
        # Process each section
        for section_idx, section in enumerate(doc.sections):
            section_slug = section.slug if hasattr(section, 'slug') else f"section_{section_idx}"
            current_section = section_slug
            
            # Add section header as potential chunk
            if hasattr(section, 'title'):
                header_text = f"# {section.title}\n"
                header_tokens = self.token_counter.count(header_text)
                
                # Flush buffer if adding header would exceed limit
                if current_text_buffer and current_tokens + header_tokens > self.config.max_tokens:
                    chunks.append(self._create_text_chunk(
                        current_text_buffer,
                        source_file,
                        current_section,
                        len(chunks)
                    ))
                    current_text_buffer = []
                    current_tokens = 0
                
                current_text_buffer.append(header_text)
                current_tokens += header_tokens
            
            # Process section content
            if hasattr(section, 'content'):
                chunks.extend(self._process_section_content(
                    section.content,
                    section_slug,
                    source_file,
                    len(chunks)
                ))
        
        # Process code examples
        if hasattr(doc, 'full_examples'):
            for example in doc.full_examples:
                example_chunks = self._process_code_example(
                    example,
                    source_file,
                    len(chunks)
                )
                chunks.extend(example_chunks)
        elif hasattr(doc, 'code_blocks'):
            for block in doc.code_blocks:
                block_chunk = self._process_code_block(
                    block,
                    source_file,
                    len(chunks)
                )
                if block_chunk:
                    chunks.append(block_chunk)
        
        # Flush any remaining buffer
        if current_text_buffer:
            chunks.append(self._create_text_chunk(
                current_text_buffer,
                source_file,
                current_section,
                len(chunks)
            ))
        
        # Add relationships and overlaps
        return self._add_chunk_relationships(chunks)
    
    def _chunk_sectioned_document(self, doc: Any) -> List[Chunk]:
        """Chunk a document with sections.
        
        Args:
            doc: Document with sections attribute
            
        Returns:
            List of chunks
        """
        chunks = []
        source_file = getattr(doc, 'source_file', 'document')
        
        for section_idx, section in enumerate(doc.sections):
            # Get the actual content text, not the Pydantic representation
            if hasattr(section, 'content'):
                section_text = section.content
            else:
                section_text = str(section)
            section_slug = getattr(section, 'slug', f"section_{section_idx}")
            
            # Check if section fits in one chunk
            section_tokens = self.token_counter.count(section_text)
            
            if section_tokens <= self.config.max_tokens:
                # Keep section together
                chunks.append(self._create_section_chunk(
                    section_text,
                    section_slug,
                    source_file,
                    len(chunks)
                ))
            else:
                # Split section intelligently
                section_chunks = self._split_large_section(
                    section_text,
                    section_slug,
                    source_file,
                    len(chunks)
                )
                chunks.extend(section_chunks)
        
        return self._add_chunk_relationships(chunks)
    
    def _process_section_content(
        self,
        content: str,
        section_slug: str,
        source_file: str,
        start_index: int
    ) -> List[Chunk]:
        """Process content within a section.
        
        Args:
            content: Section content text
            section_slug: Section identifier
            source_file: Source file name
            start_index: Starting chunk index
            
        Returns:
            List of chunks for this section
        """
        chunks = []
        
        # Split content by paragraphs if configured
        if self.config.respect_paragraph_boundaries:
            paragraphs = content.split('\n\n')
            
            current_buffer = []
            current_tokens = 0
            
            for para in paragraphs:
                para_tokens = self.token_counter.count(para)
                
                # Check if adding paragraph exceeds limit
                if current_tokens + para_tokens > self.config.max_tokens:
                    if current_buffer:
                        # Create chunk from buffer
                        chunks.append(self._create_text_chunk(
                            current_buffer,
                            source_file,
                            section_slug,
                            start_index + len(chunks)
                        ))
                        current_buffer = []
                        current_tokens = 0
                    
                    # Check if paragraph itself is too large
                    if para_tokens > self.config.max_tokens:
                        # Split paragraph at sentence boundaries
                        para_chunks = self._split_paragraph(
                            para,
                            section_slug,
                            source_file,
                            start_index + len(chunks)
                        )
                        chunks.extend(para_chunks)
                    else:
                        current_buffer.append(para)
                        current_tokens = para_tokens
                else:
                    current_buffer.append(para)
                    current_tokens += para_tokens
            
            # Flush remaining buffer
            if current_buffer:
                chunks.append(self._create_text_chunk(
                    current_buffer,
                    source_file,
                    section_slug,
                    start_index + len(chunks)
                ))
        else:
            # Simple token-based splitting
            text_chunks = self.token_counter.split_at_token_limit(
                content,
                self.config.max_tokens,
                self.config.overlap_tokens
            )
            
            for i, text in enumerate(text_chunks):
                chunks.append(self._create_text_chunk(
                    [text],
                    source_file,
                    section_slug,
                    start_index + len(chunks)
                ))
        
        return chunks
    
    def _process_code_example(
        self,
        example: Any,
        source_file: str,
        chunk_index: int
    ) -> List[Chunk]:
        """Process a code example into chunks.
        
        Args:
            example: Code example object
            source_file: Source file name
            chunk_index: Current chunk index
            
        Returns:
            List of chunks (usually just one unless code is very large)
        """
        chunks = []
        
        # Build content with context
        content_parts = []
        
        # Add context before if available
        if hasattr(example, 'context_before') and example.context_before:
            content_parts.append(example.context_before)
        
        # Add the code
        lang = example.language if hasattr(example, 'language') else ""
        content_parts.append(f"```{lang}")
        content_parts.append(example.content)
        content_parts.append("```")
        
        # Add context after if available
        if hasattr(example, 'context_after') and example.context_after:
            content_parts.append(example.context_after)
        
        full_content = "\n".join(content_parts)
        content_tokens = self.token_counter.count(full_content)
        
        # Determine example type
        example_type = "neutral"
        if hasattr(example, 'example_type'):
            example_type = str(example.example_type.value if hasattr(example.example_type, 'value') else example.example_type)
        
        # Create metadata
        metadata = ChunkMetadata(
            source_file=source_file,
            section=example.section_slug if hasattr(example, 'section_slug') else None,
            has_code=True,
            code_languages=[lang] if lang else [],
            example_types=[example_type],
            chunk_index=chunk_index,
            total_chunks=0,  # Will be updated later
            start_line=example.line_start if hasattr(example, 'line_start') else None
        )
        
        # Check if code fits in one chunk
        if content_tokens <= self.config.max_tokens:
            # Keep code example together
            chunk = Chunk(
                chunk_id=self._generate_chunk_id(full_content, chunk_index),
                content=full_content,
                chunk_type=ChunkType.CODE,
                token_count=content_tokens,
                encoding_model=self.config.encoding_model,
                metadata=metadata
            )
            chunks.append(chunk)
        else:
            # Code is too large - special handling
            # Try to keep at least the code together without context
            code_only = f"```{lang}\n{example.content}\n```"
            code_tokens = self.token_counter.count(code_only)
            
            if code_tokens <= self.config.max_tokens:
                # Create chunk with just code
                chunk = Chunk(
                    chunk_id=self._generate_chunk_id(code_only, chunk_index),
                    content=code_only,
                    chunk_type=ChunkType.CODE,
                    token_count=code_tokens,
                    encoding_model=self.config.encoding_model,
                    metadata=metadata
                )
                chunks.append(chunk)
                
                # Add context as separate chunks if needed
                if example.context_before:
                    context_chunk = self._create_text_chunk(
                        [example.context_before],
                        source_file,
                        metadata.section,
                        chunk_index + len(chunks)
                    )
                    chunks.append(context_chunk)
            else:
                # Code itself is too large - must split (rare case)
                # This violates our "never split code" principle but necessary
                print(f"Warning: Code example too large ({code_tokens} tokens), must split")
                code_chunks = self._split_large_code(
                    example.content,
                    lang,
                    metadata,
                    chunk_index
                )
                chunks.extend(code_chunks)
        
        return chunks
    
    def _process_code_block(
        self,
        block: Any,
        source_file: str,
        chunk_index: int
    ) -> Optional[Chunk]:
        """Process a simple code block.
        
        Args:
            block: Code block object
            source_file: Source file name
            chunk_index: Chunk index
            
        Returns:
            Chunk or None if block is empty
        """
        if not block.content:
            return None
        
        lang = block.language if hasattr(block, 'language') else ""
        content = f"```{lang}\n{block.content}\n```"
        
        metadata = ChunkMetadata(
            source_file=source_file,
            section=block.section_slug if hasattr(block, 'section_slug') else None,
            has_code=True,
            code_languages=[lang] if lang else [],
            chunk_index=chunk_index,
            total_chunks=0,
            start_line=block.line_start if hasattr(block, 'line_start') else None
        )
        
        return Chunk(
            chunk_id=self._generate_chunk_id(content, chunk_index),
            content=content,
            chunk_type=ChunkType.CODE,
            token_count=self.token_counter.count(content),
            encoding_model=self.config.encoding_model,
            metadata=metadata
        )
    
    def _create_text_chunk(
        self,
        text_parts: List[str],
        source_file: str,
        section: Optional[str],
        chunk_index: int
    ) -> Chunk:
        """Create a text chunk from parts.
        
        Args:
            text_parts: List of text parts to combine
            source_file: Source file name
            section: Section slug
            chunk_index: Chunk index
            
        Returns:
            Text chunk
        """
        content = "\n\n".join(text_parts)
        
        metadata = ChunkMetadata(
            source_file=source_file,
            section=section,
            has_code=self._detect_code(content),
            chunk_index=chunk_index,
            total_chunks=0
        )
        
        return Chunk(
            chunk_id=self._generate_chunk_id(content, chunk_index),
            content=content,
            chunk_type=self._detect_chunk_type(content),
            token_count=self.token_counter.count(content),
            encoding_model=self.config.encoding_model,
            metadata=metadata
        )
    
    def _create_section_chunk(
        self,
        content: str,
        section_slug: str,
        source_file: str,
        chunk_index: int
    ) -> Chunk:
        """Create a chunk for an entire section.
        
        Args:
            content: Section content
            section_slug: Section identifier
            source_file: Source file name
            chunk_index: Chunk index
            
        Returns:
            Section chunk
        """
        metadata = ChunkMetadata(
            source_file=source_file,
            section=section_slug,
            has_code=self._detect_code(content),
            chunk_index=chunk_index,
            total_chunks=0
        )
        
        return Chunk(
            chunk_id=self._generate_chunk_id(content, chunk_index),
            content=content,
            chunk_type=ChunkType.SECTION_HEADER if content.startswith("#") else self._detect_chunk_type(content),
            token_count=self.token_counter.count(content),
            encoding_model=self.config.encoding_model,
            metadata=metadata
        )
    
    def _split_paragraph(
        self,
        paragraph: str,
        section: str,
        source_file: str,
        start_index: int
    ) -> List[Chunk]:
        """Split a large paragraph at sentence boundaries.
        
        Args:
            paragraph: Paragraph text
            section: Section slug
            source_file: Source file name
            start_index: Starting chunk index
            
        Returns:
            List of chunks
        """
        chunks = []
        
        # Simple sentence splitting (can be improved with NLTK or spaCy)
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        current_buffer = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.token_counter.count(sentence)
            
            if current_tokens + sentence_tokens > self.config.max_tokens:
                if current_buffer:
                    chunks.append(self._create_text_chunk(
                        current_buffer,
                        source_file,
                        section,
                        start_index + len(chunks)
                    ))
                    current_buffer = []
                    current_tokens = 0
                
                # Add sentence (may be truncated if too long)
                if sentence_tokens > self.config.max_tokens:
                    # Split sentence at word boundaries as last resort
                    words = sentence.split()
                    word_buffer = []
                    word_tokens = 0
                    
                    for word in words:
                        word_token_count = self.token_counter.count(word + " ")
                        if word_tokens + word_token_count > self.config.max_tokens:
                            if word_buffer:
                                chunks.append(self._create_text_chunk(
                                    [" ".join(word_buffer)],
                                    source_file,
                                    section,
                                    start_index + len(chunks)
                                ))
                                word_buffer = []
                                word_tokens = 0
                        word_buffer.append(word)
                        word_tokens += word_token_count
                    
                    if word_buffer:
                        current_buffer = [" ".join(word_buffer)]
                        current_tokens = self.token_counter.count(current_buffer[0])
                else:
                    current_buffer.append(sentence)
                    current_tokens = sentence_tokens
            else:
                current_buffer.append(sentence)
                current_tokens += sentence_tokens
        
        # Flush remaining buffer
        if current_buffer:
            chunks.append(self._create_text_chunk(
                current_buffer,
                source_file,
                section,
                start_index + len(chunks)
            ))
        
        return chunks
    
    def _split_large_section(
        self,
        section_text: str,
        section_slug: str,
        source_file: str,
        start_index: int
    ) -> List[Chunk]:
        """Split a large section into multiple chunks.
        
        Args:
            section_text: Section text
            section_slug: Section identifier
            source_file: Source file name
            start_index: Starting chunk index
            
        Returns:
            List of chunks
        """
        # Use the process_section_content method
        return self._process_section_content(
            section_text,
            section_slug,
            source_file,
            start_index
        )
    
    def _split_large_code(
        self,
        code: str,
        language: str,
        metadata: ChunkMetadata,
        start_index: int
    ) -> List[Chunk]:
        """Split large code block (last resort).
        
        Args:
            code: Code content
            language: Programming language
            metadata: Base metadata
            start_index: Starting chunk index
            
        Returns:
            List of code chunks
        """
        chunks = []
        
        # Try to split at function/class boundaries for Python
        if language.lower() in ['python', 'py']:
            # Simple regex for Python functions/classes
            parts = re.split(r'\n(?=(?:def |class |async def ))', code)
        else:
            # Split at newlines as fallback
            lines = code.split('\n')
            parts = []
            current_part = []
            current_tokens = 0
            
            for line in lines:
                line_tokens = self.token_counter.count(line + "\n")
                if current_tokens + line_tokens > self.config.max_tokens - 20:  # Leave room for ``` markers
                    if current_part:
                        parts.append('\n'.join(current_part))
                        current_part = []
                        current_tokens = 0
                current_part.append(line)
                current_tokens += line_tokens
            
            if current_part:
                parts.append('\n'.join(current_part))
        
        # Create chunks from parts
        for i, part in enumerate(parts):
            part_content = f"```{language}\n{part}\n```"
            
            chunk_metadata = ChunkMetadata(**metadata.model_dump())
            chunk_metadata.chunk_index = start_index + i
            
            chunk = Chunk(
                chunk_id=self._generate_chunk_id(part_content, start_index + i),
                content=part_content,
                chunk_type=ChunkType.CODE,
                token_count=self.token_counter.count(part_content),
                encoding_model=self.config.encoding_model,
                metadata=chunk_metadata
            )
            chunks.append(chunk)
        
        return chunks