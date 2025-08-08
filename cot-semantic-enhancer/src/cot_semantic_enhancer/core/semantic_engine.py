"""Main semantic enhancement engine."""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import asyncio
from dataclasses import dataclass

from .embedding_provider import EmbeddingProvider
from .vector_store import VectorStore, SearchResult


@dataclass
class SemanticMatch:
    """Result of semantic matching."""
    text: str
    score: float
    metadata: Dict[str, Any]
    explanation: Optional[str] = None


@dataclass
class Contradiction:
    """Detected contradiction between statements."""
    statement1: str
    statement2: str
    confidence: float
    type: str  # "negation", "antonym", "semantic_opposition"
    explanation: str


class SemanticEngine:
    """Main semantic enhancement engine.
    
    Coordinates embedding generation, vector storage, and semantic analysis
    to provide comprehensive semantic capabilities for CoT reasoning.
    """
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        contradiction_detector: Optional[Any] = None,
        similarity_calculator: Optional[Any] = None
    ):
        """Initialize semantic engine.
        
        Args:
            embedding_provider: Provider for generating embeddings
            vector_store: Store for managing vectors
            contradiction_detector: Optional contradiction detection component
            similarity_calculator: Optional similarity calculation component
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.contradiction_detector = contradiction_detector
        self.similarity_calculator = similarity_calculator
        
        # Track statistics
        self._stats = {
            "total_embeddings": 0,
            "total_searches": 0,
            "total_contradictions_checked": 0
        }
    
    async def add_knowledge(
        self,
        texts: List[str],
        metadata: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add knowledge to the semantic store.
        
        Args:
            texts: List of texts to add
            metadata: Optional metadata for each text
            ids: Optional IDs for texts
            
        Returns:
            List of IDs for added knowledge
        """
        # Generate embeddings
        embeddings = await self.embedding_provider.embed_batch(texts)
        
        # Validate dimensions
        if not self.embedding_provider.validate_dimension(embeddings):
            raise ValueError(
                f"Embedding dimension mismatch. Expected {self.embedding_provider.dimension}, "
                f"got {embeddings.shape[1]}"
            )
        
        # Prepare metadata
        if metadata is None:
            metadata = []
        
        # Ensure metadata for each text
        final_metadata = []
        for i, text in enumerate(texts):
            meta = metadata[i] if i < len(metadata) else {}
            meta["text"] = text
            meta["added_at"] = datetime.utcnow().isoformat()
            meta["provider"] = self.embedding_provider.model_name
            final_metadata.append(meta)
        
        # Add to vector store
        ids = await self.vector_store.add(embeddings, final_metadata, ids)
        
        # Update statistics
        self._stats["total_embeddings"] += len(texts)
        
        return ids
    
    async def semantic_search(
        self,
        query: str,
        k: int = 5,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None,
        explain: bool = False
    ) -> List[SemanticMatch]:
        """Perform semantic similarity search.
        
        Args:
            query: Query text
            k: Number of results
            threshold: Minimum similarity threshold
            filter: Optional metadata filter
            explain: Whether to generate explanations
            
        Returns:
            List of semantic matches
        """
        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_async(query)
        if len(query_embedding.shape) == 2:
            query_embedding = query_embedding[0]
        
        # Search vector store
        results = await self.vector_store.similarity_search(
            query_embedding, threshold, k * 2, filter
        )
        
        # Convert to semantic matches
        matches = []
        for result in results[:k]:
            match = SemanticMatch(
                text=result.metadata.get("text", ""),
                score=result.score,
                metadata=result.metadata
            )
            
            if explain and self.similarity_calculator:
                match.explanation = self._generate_explanation(query, match.text, match.score)
            
            matches.append(match)
        
        # Update statistics
        self._stats["total_searches"] += 1
        
        return matches
    
    async def detect_contradictions(
        self,
        statements: List[str],
        threshold: float = 0.8
    ) -> List[Contradiction]:
        """Detect contradictions in statements.
        
        Args:
            statements: List of statements to check
            threshold: Confidence threshold for contradictions
            
        Returns:
            List of detected contradictions
        """
        if not self.contradiction_detector:
            raise ValueError("Contradiction detector not configured")
        
        # Generate embeddings for all statements
        embeddings = await self.embedding_provider.embed_batch(statements)
        
        # Use contradiction detector
        contradictions = await self.contradiction_detector.detect(
            statements, embeddings, threshold
        )
        
        # Update statistics
        self._stats["total_contradictions_checked"] += len(statements)
        
        return contradictions
    
    async def find_similar_facts(
        self,
        fact: str,
        k: int = 5,
        include_self: bool = False
    ) -> List[SemanticMatch]:
        """Find facts similar to the given one.
        
        Args:
            fact: Reference fact
            k: Number of similar facts to find
            include_self: Whether to include the fact itself
            
        Returns:
            List of similar facts
        """
        # Search for similar items
        results = await self.semantic_search(fact, k + 1 if not include_self else k)
        
        # Filter out self if needed
        if not include_self:
            results = [r for r in results if r.text != fact][:k]
        
        return results
    
    async def cluster_statements(
        self,
        statements: List[str],
        n_clusters: Optional[int] = None,
        min_similarity: float = 0.7
    ) -> List[List[str]]:
        """Cluster statements by semantic similarity.
        
        Args:
            statements: List of statements to cluster
            n_clusters: Number of clusters (auto-detect if None)
            min_similarity: Minimum similarity for same cluster
            
        Returns:
            List of statement clusters
        """
        # Generate embeddings
        embeddings = await self.embedding_provider.embed_batch(statements)
        
        # Simple clustering based on similarity threshold
        clusters = []
        assigned = set()
        
        for i, statement in enumerate(statements):
            if i in assigned:
                continue
            
            # Start new cluster
            cluster = [statement]
            assigned.add(i)
            
            # Find similar statements
            for j in range(i + 1, len(statements)):
                if j in assigned:
                    continue
                
                similarity = self.vector_store.calculate_similarity(
                    embeddings[i], embeddings[j]
                )
                
                if similarity >= min_similarity:
                    cluster.append(statements[j])
                    assigned.add(j)
            
            clusters.append(cluster)
            
            # Stop if we have enough clusters
            if n_clusters and len(clusters) >= n_clusters:
                # Add remaining as single-item clusters
                for j in range(len(statements)):
                    if j not in assigned:
                        clusters.append([statements[j]])
                break
        
        return clusters
    
    async def verify_consistency(
        self,
        new_fact: str,
        existing_facts: Optional[List[str]] = None,
        threshold: float = 0.8
    ) -> Tuple[bool, List[Contradiction]]:
        """Verify if a new fact is consistent with existing knowledge.
        
        Args:
            new_fact: New fact to verify
            existing_facts: Existing facts to check against
            threshold: Contradiction threshold
            
        Returns:
            Tuple of (is_consistent, list_of_contradictions)
        """
        # If no existing facts provided, search for related ones
        if existing_facts is None:
            similar = await self.semantic_search(new_fact, k=10)
            existing_facts = [m.text for m in similar]
        
        if not existing_facts:
            return True, []
        
        # Check for contradictions
        all_statements = [new_fact] + existing_facts
        contradictions = await self.detect_contradictions(all_statements, threshold)
        
        # Filter for contradictions involving the new fact
        new_fact_contradictions = [
            c for c in contradictions
            if new_fact in (c.statement1, c.statement2)
        ]
        
        is_consistent = len(new_fact_contradictions) == 0
        return is_consistent, new_fact_contradictions
    
    async def embed_with_context(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> np.ndarray:
        """Generate embedding with additional context.
        
        Args:
            text: Text to embed
            context: Additional context information
            
        Returns:
            Embedding vector
        """
        # Enhance text with context if provided
        if context:
            context_str = " ".join(f"{k}:{v}" for k, v in context.items())
            enhanced_text = f"{text} [CONTEXT: {context_str}]"
        else:
            enhanced_text = text
        
        # Generate embedding
        embedding = await self.embedding_provider.embed_async(enhanced_text)
        
        if len(embedding.shape) == 2:
            embedding = embedding[0]
        
        return embedding
    
    def _generate_explanation(self, query: str, match: str, score: float) -> str:
        """Generate explanation for similarity match.
        
        Args:
            query: Query text
            match: Matched text
            score: Similarity score
            
        Returns:
            Explanation string
        """
        if score > 0.95:
            level = "nearly identical"
        elif score > 0.85:
            level = "very similar"
        elif score > 0.75:
            level = "similar"
        else:
            level = "somewhat related"
        
        return f"The matched text is {level} to the query (score: {score:.3f})"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics.
        
        Returns:
            Dictionary with statistics
        """
        vector_stats = await self.vector_store.get_stats()
        cache_stats = self.embedding_provider.get_cache_stats()
        
        return {
            "engine": self._stats,
            "vector_store": vector_stats,
            "embedding_cache": cache_stats
        }
    
    async def clear_all(self) -> bool:
        """Clear all data from the engine.
        
        Returns:
            True if successful
        """
        # Clear vector store
        success = await self.vector_store.clear()
        
        # Clear embedding cache
        self.embedding_provider.clear_cache()
        
        # Reset statistics
        self._stats = {
            "total_embeddings": 0,
            "total_searches": 0,
            "total_contradictions_checked": 0
        }
        
        return success