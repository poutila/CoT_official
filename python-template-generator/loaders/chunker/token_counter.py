"""Token counting utilities using tiktoken."""

import tiktoken
from typing import List, Dict, Optional, Tuple
from functools import lru_cache


class TokenCounter:
    """Efficient token counting with caching."""
    
    def __init__(self, encoding_model: str = "cl100k_base"):
        """Initialize token counter with specified encoding.
        
        Args:
            encoding_model: Name of tiktoken encoding to use.
                           Common options: "cl100k_base" (GPT-3.5/4),
                                         "p50k_base" (Codex),
                                         "r50k_base" (GPT-2/3)
        """
        self.encoding_model = encoding_model
        self.encoder = tiktoken.get_encoding(encoding_model)
        self._cache = {}
    
    def count(self, text: str) -> int:
        """Count tokens in text with caching.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        # Use hash for cache key to handle large texts
        cache_key = hash(text)
        
        if cache_key not in self._cache:
            tokens = self.encoder.encode(text)
            self._cache[cache_key] = len(tokens)
            
            # Limit cache size to prevent memory issues
            if len(self._cache) > 10000:
                # Remove oldest entries (simple FIFO)
                self._cache = dict(list(self._cache.items())[-5000:])
        
        return self._cache[cache_key]
    
    def count_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts efficiently.
        
        Args:
            texts: List of texts to count
            
        Returns:
            List of token counts
        """
        return [self.count(text) for text in texts]
    
    def encode(self, text: str) -> List[int]:
        """Encode text to token IDs.
        
        Args:
            text: Text to encode
            
        Returns:
            List of token IDs
        """
        return self.encoder.encode(text)
    
    def decode(self, tokens: List[int]) -> str:
        """Decode token IDs back to text.
        
        Args:
            tokens: List of token IDs
            
        Returns:
            Decoded text
        """
        return self.encoder.decode(tokens)
    
    def split_at_token_limit(
        self, 
        text: str, 
        max_tokens: int,
        overlap_tokens: int = 0
    ) -> List[str]:
        """Split text at token boundaries with optional overlap.
        
        Args:
            text: Text to split
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Number of tokens to overlap between chunks
            
        Returns:
            List of text chunks
        """
        tokens = self.encode(text)
        chunks = []
        
        if len(tokens) <= max_tokens:
            return [text]
        
        # Ensure overlap is less than max_tokens to avoid infinite loops
        overlap_tokens = min(overlap_tokens, max_tokens - 1)
        
        start = 0
        prev_start = -1
        while start < len(tokens):
            # Safety check for infinite loop
            if start == prev_start:
                break
            prev_start = start
            
            # Calculate end position
            end = min(start + max_tokens, len(tokens))
            
            # Extract chunk tokens
            chunk_tokens = tokens[start:end]
            
            # Add overlap from previous chunk if not first chunk
            if start > 0 and overlap_tokens > 0:
                overlap_start = max(0, start - overlap_tokens)
                chunk_tokens = tokens[overlap_start:end]
            
            # Decode and add chunk
            chunk_text = self.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start position - ensure we make progress
            if overlap_tokens > 0 and end < len(tokens):
                # Move forward by at least (max_tokens - overlap_tokens), but at least 1
                start = max(start + 1, end - overlap_tokens)
            else:
                start = end
        
        return chunks
    
    def find_optimal_split_point(
        self,
        text: str,
        target_tokens: int,
        look_back: int = 50,
        look_forward: int = 50
    ) -> int:
        """Find optimal split point near target token count.
        
        Tries to split at natural boundaries (sentences, paragraphs).
        
        Args:
            text: Text to find split point in
            target_tokens: Target number of tokens
            look_back: Tokens to look back for boundary
            look_forward: Tokens to look forward for boundary
            
        Returns:
            Character index for split point
        """
        tokens = self.encode(text)
        
        if len(tokens) <= target_tokens:
            return len(text)
        
        # Get approximate character position
        target_text = self.decode(tokens[:target_tokens])
        base_pos = len(target_text)
        
        # Look for natural boundaries
        search_start = max(0, base_pos - look_back * 4)  # Approximate chars per token
        search_end = min(len(text), base_pos + look_forward * 4)
        search_text = text[search_start:search_end]
        
        # Priority: paragraph > sentence > word
        boundaries = [
            ('\n\n', 3),  # Paragraph
            ('.\n', 2),   # Sentence with newline
            ('. ', 2),    # Sentence
            ('! ', 2),    # Exclamation
            ('? ', 2),    # Question
            ('\n', 1),    # Line break
            (' ', 0),     # Word
        ]
        
        best_pos = base_pos
        best_score = -1
        
        for boundary, score in boundaries:
            # Find all occurrences of this boundary
            pos = search_start
            while True:
                pos = text.find(boundary, pos, search_end)
                if pos == -1:
                    break
                
                # Check if this position is better
                actual_tokens = self.count(text[:pos + len(boundary)])
                distance = abs(actual_tokens - target_tokens)
                
                # Score based on boundary type and distance
                boundary_score = score * 100 - distance
                
                if boundary_score > best_score:
                    best_score = boundary_score
                    best_pos = pos + len(boundary)
                
                pos += 1
        
        return best_pos
    
    def estimate_chunks_needed(
        self,
        text: str,
        max_tokens: int,
        overlap_tokens: int = 0
    ) -> int:
        """Estimate number of chunks needed for text.
        
        Args:
            text: Text to estimate for
            max_tokens: Maximum tokens per chunk
            overlap_tokens: Overlap between chunks
            
        Returns:
            Estimated number of chunks
        """
        total_tokens = self.count(text)
        
        if total_tokens <= max_tokens:
            return 1
        
        # Account for overlap
        effective_tokens_per_chunk = max_tokens - overlap_tokens
        chunks = (total_tokens - overlap_tokens) / effective_tokens_per_chunk
        
        return max(1, int(chunks) + (1 if chunks % 1 > 0 else 0))
    
    def clear_cache(self):
        """Clear the token count cache."""
        self._cache.clear()
    
    @property
    def cache_size(self) -> int:
        """Get current cache size."""
        return len(self._cache)
    
    @staticmethod
    @lru_cache(maxsize=10)
    def get_encoding_info(encoding_model: str) -> Dict[str, any]:
        """Get information about a tiktoken encoding.
        
        Args:
            encoding_model: Name of encoding
            
        Returns:
            Dictionary with encoding information
        """
        encoding = tiktoken.get_encoding(encoding_model)
        
        return {
            "name": encoding_model,
            "max_token_value": encoding.max_token_value,
            "n_vocab": encoding.n_vocab if hasattr(encoding, 'n_vocab') else None,
            "special_tokens": list(encoding._special_tokens.keys()) if hasattr(encoding, '_special_tokens') else [],
        }
    
    @staticmethod
    def estimate_tokens(text: str, chars_per_token: float = 4.0) -> int:
        """Quick token estimation without encoding.
        
        Useful for rough estimates without the overhead of actual encoding.
        
        Args:
            text: Text to estimate
            chars_per_token: Average characters per token (default 4.0 for English)
            
        Returns:
            Estimated token count
        """
        # Adjust for whitespace and punctuation
        word_count = len(text.split())
        char_count = len(text)
        
        # Use combination of word and character count for better estimate
        token_estimate = max(
            word_count * 1.3,  # Words typically become ~1.3 tokens
            char_count / chars_per_token
        )
        
        return int(token_estimate)