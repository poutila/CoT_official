"""Sentence Transformer embedding provider."""

from typing import List, Optional, Union
import numpy as np
import logging
from pathlib import Path

from .base_provider import BaseEmbeddingProvider
from .models import EmbeddingProviderConfig, EmbeddingProviderType

# Set up logging
logger = logging.getLogger(__name__)


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Embedding provider using sentence-transformers library.
    
    This provider uses the sentence-transformers library to generate
    high-quality embeddings for semantic similarity tasks.
    
    Popular models:
    - all-MiniLM-L6-v2: Fast, good quality (384 dims)
    - all-mpnet-base-v2: Best quality (768 dims)
    - all-MiniLM-L12-v2: Balanced (384 dims)
    - multi-qa-MiniLM-L6-cos-v1: Optimized for Q&A (384 dims)
    """
    
    def __init__(
        self,
        config: Optional[EmbeddingProviderConfig] = None,
        model_name: Optional[str] = None
    ):
        """Initialize the Sentence Transformer provider.
        
        Args:
            config: Provider configuration
            model_name: Override model name from config
        """
        # Set default config if not provided
        if config is None:
            config = EmbeddingProviderConfig(
                provider_type=EmbeddingProviderType.SENTENCE_TRANSFORMER,
                model_name=model_name or "all-MiniLM-L6-v2"
            )
        elif model_name:
            config.model_name = model_name
        
        # Store model reference before calling parent init
        self.model = None
        
        super().__init__(config)
    
    def _initialize_model(self) -> None:
        """Initialize the Sentence Transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with: uv add sentence-transformers"
            )
        
        logger.info(f"Loading SentenceTransformer model: {self.model_name}")
        
        # Determine device
        device = self.config.device
        if device == "auto" or device is None:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model
        try:
            self.model = SentenceTransformer(
                self.model_name,
                device=device
            )
            
            # Set max sequence length if specified
            if self.config.max_seq_length:
                self.model.max_seq_length = self.config.max_seq_length
            
            # Auto-detect dimension if not set
            if self.dimension is None:
                # Generate a test embedding to get dimension
                test_embedding = self.model.encode("test", convert_to_numpy=True)
                self.dimension = len(test_embedding)
            
            logger.info(
                f"Model loaded successfully. "
                f"Dimension: {self.dimension}, "
                f"Device: {device}, "
                f"Max sequence length: {self.model.max_seq_length}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise
    
    def _encode_single(self, text: str) -> np.ndarray:
        """Encode a single text to embedding.
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding as numpy array
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # Encode with sentence-transformers
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=False,  # We handle normalization ourselves
            show_progress_bar=False
        )
        
        return embedding
    
    def _encode_batch(self, texts: List[str]) -> np.ndarray:
        """Encode a batch of texts to embeddings.
        
        Args:
            texts: List of texts to encode
            
        Returns:
            Embeddings as numpy array of shape (batch_size, dimension)
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # Encode batch with sentence-transformers
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False,  # We handle normalization ourselves
            batch_size=self.config.batch_size,
            show_progress_bar=False
        )
        
        return embeddings
    
    def encode_with_pooling(
        self,
        texts: Union[str, List[str]],
        pooling_strategy: str = "mean"
    ) -> np.ndarray:
        """Encode with custom pooling strategy.
        
        Args:
            texts: Text or list of texts
            pooling_strategy: Pooling strategy (mean, max, cls)
            
        Returns:
            Embeddings as numpy array
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        # This is an advanced feature that requires accessing token embeddings
        # For now, we just use the default pooling from the model
        if isinstance(texts, str):
            return self._encode_single(texts)
        else:
            return self._encode_batch(texts)
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {"error": "Model not initialized"}
        
        info = {
            "model_name": self.model_name,
            "dimension": self.dimension,
            "max_seq_length": self.model.max_seq_length,
            "device": str(self.model.device),
        }
        
        # Add tokenizer info if available
        if hasattr(self.model, 'tokenizer'):
            info["tokenizer"] = {
                "type": type(self.model.tokenizer).__name__,
                "vocab_size": len(self.model.tokenizer) if hasattr(self.model.tokenizer, '__len__') else "unknown"
            }
        
        # Add model architecture info if available  
        if hasattr(self.model[0], 'auto_model'):
            info["architecture"] = type(self.model[0].auto_model).__name__
        
        return info
    
    def save_model(self, path: Union[str, Path]) -> None:
        """Save the model to disk.
        
        Args:
            path: Path to save the model
        """
        if self.model is None:
            raise RuntimeError("Model not initialized")
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        self.model.save(str(path))
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load_model(cls, path: Union[str, Path]) -> 'SentenceTransformerProvider':
        """Load a model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            Initialized provider with loaded model
        """
        from sentence_transformers import SentenceTransformer
        
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model path does not exist: {path}")
        
        # Load the model
        model = SentenceTransformer(str(path))
        
        # Create provider with loaded model
        config = EmbeddingProviderConfig(
            provider_type=EmbeddingProviderType.SENTENCE_TRANSFORMER,
            model_name=str(path)
        )
        
        provider = cls(config)
        provider.model = model
        
        # Auto-detect dimension
        test_embedding = model.encode("test", convert_to_numpy=True)
        provider.dimension = len(test_embedding)
        
        return provider
    
    def _check_truncation(self, text: str) -> bool:
        """Check if text will be truncated.
        
        Args:
            text: Text to check
            
        Returns:
            True if text will be truncated
        """
        if self.model is None:
            return False
        
        # Use tokenizer to check actual token count
        if hasattr(self.model, 'tokenizer'):
            tokens = self.model.tokenizer.tokenize(text)
            return len(tokens) > self.model.max_seq_length
        
        # Fallback to character-based estimation
        return super()._check_truncation(text)
    
    @staticmethod
    def list_available_models() -> List[str]:
        """List commonly used sentence transformer models.
        
        Returns:
            List of model names
        """
        return [
            # English models
            "all-MiniLM-L6-v2",  # 384 dims, fast
            "all-MiniLM-L12-v2",  # 384 dims, balanced
            "all-mpnet-base-v2",  # 768 dims, best quality
            "multi-qa-MiniLM-L6-cos-v1",  # 384 dims, Q&A optimized
            "multi-qa-mpnet-base-cos-v1",  # 768 dims, Q&A optimized
            "multi-qa-distilbert-cos-v1",  # 768 dims, Q&A
            "all-distilroberta-v1",  # 768 dims
            "all-roberta-large-v1",  # 1024 dims, highest quality
            
            # Multilingual models
            "paraphrase-multilingual-MiniLM-L12-v2",  # 384 dims
            "paraphrase-multilingual-mpnet-base-v2",  # 768 dims
            "distiluse-base-multilingual-cased-v2",  # 512 dims
            
            # Code-specific models
            "flax-sentence-embeddings/st-codesearch-distilroberta-base",  # For code
            
            # Domain-specific models
            "pritamdeka/S-PubMedBert-MS-MARCO",  # Medical
            "sentence-transformers/allenai-specter",  # Scientific papers
        ]