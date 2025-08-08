"""Adapter classes for LangChain integration.

These adapters allow our custom components to work with LangChain's interfaces.
They're designed as a bridge for future integration without modifying our core components.
"""

from abc import ABC
from typing import Any

from .models import Document


class BaseTextSplitterAdapter(ABC):
    """Adapter to make our chunker compatible with LangChain's TextSplitter interface."""

    def __init__(self, chunker: Any) -> None:
        """Initialize with our custom chunker.

        Args:
            chunker: Our SemanticChunker instance
        """
        self.chunker = chunker

    def split_text(self, text: str) -> list[str]:
        """Split text into chunks (LangChain compatible).

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = self.chunker.chunk_text(text)
        return [chunk.content for chunk in chunks]

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks (LangChain compatible).

        Args:
            documents: List of documents to split

        Returns:
            List of chunked documents
        """
        all_chunks = []

        for doc in documents:
            # Use our chunker
            chunks = self.chunker.chunk_text(
                doc.page_content, source_file=doc.metadata.get("source", "unknown")
            )

            # Convert to Document format
            for chunk in chunks:
                chunk_doc = Document(
                    page_content=chunk.content,
                    metadata={
                        **doc.metadata,  # Preserve original metadata
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.metadata.chunk_index,
                        "token_count": chunk.token_count,
                        "chunk_type": chunk.chunk_type.value,
                    },
                )
                all_chunks.append(chunk_doc)

        return all_chunks

    def create_documents(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None
    ) -> list[Document]:
        """Create documents from texts (LangChain compatible).

        Args:
            texts: List of texts
            metadatas: Optional metadata for each text

        Returns:
            List of documents
        """
        documents = []
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            documents.append(Document(page_content=text, metadata=metadata))

        return self.split_documents(documents)


class BaseEmbeddingsAdapter(ABC):
    """Adapter to make our embedder compatible with LangChain's Embeddings interface."""

    def __init__(self, embedder: Any) -> None:
        """Initialize with our custom embedder.

        Args:
            embedder: Our SentenceTransformerProvider instance
        """
        self.embedder = embedder

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed documents (LangChain compatible).

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        batch_result = self.embedder.embed_batch(texts)
        return [emb.embedding for emb in batch_result.embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Embed a query (LangChain compatible).

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        result = self.embedder.embed(text)
        return result.embedding

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Async embed documents (LangChain compatible).

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        batch_result = await self.embedder.embed_batch_async(texts)
        return [emb.embedding for emb in batch_result.embeddings]

    async def aembed_query(self, text: str) -> list[float]:
        """Async embed a query (LangChain compatible).

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        result = await self.embedder.embed_async(text)
        return result.embedding


class BaseVectorStoreAdapter(ABC):
    """Adapter to make our vector store compatible with LangChain's VectorStore interface."""

    def __init__(self, vector_store: Any, embedder: Any) -> None:
        """Initialize with our custom vector store and embedder.

        Args:
            vector_store: Our FAISSVectorStore instance
            embedder: Our embedder for text to vector conversion
        """
        self.vector_store = vector_store
        self.embedder = embedder

    def add_texts(
        self, texts: list[str], metadatas: list[dict[str, Any]] | None = None, **kwargs
    ) -> list[str]:
        """Add texts to the vector store (LangChain compatible).

        Args:
            texts: List of texts to add
            metadatas: Optional metadata for each text
            **kwargs: Additional arguments

        Returns:
            List of IDs
        """
        # Generate embeddings
        embeddings = self.embedder.embed_batch(texts)

        # Prepare metadata
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Add text to metadata
        for i, meta in enumerate(metadatas):
            meta["text"] = texts[i]

        # Add to store
        vectors = [emb.numpy for emb in embeddings.embeddings]
        ids = self.vector_store.add_batch(vectors, metadatas)
        return list(ids) if ids else []

    def add_documents(self, documents: list[Document], **kwargs: Any) -> list[str]:
        """Add documents to the vector store (LangChain compatible).

        Args:
            documents: List of documents to add
            **kwargs: Additional arguments

        Returns:
            List of IDs
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> list[Document]:
        """Search for similar documents (LangChain compatible).

        Args:
            query: Query text
            k: Number of results
            **kwargs: Additional arguments

        Returns:
            List of similar documents
        """
        # Embed query
        query_embedding = self.embedder.embed(query)

        # Search
        results = self.vector_store.search(query_embedding.numpy, k=k)

        # Convert to documents
        documents = []
        for result in results:
            doc = Document(page_content=result.metadata.get("text", ""), metadata=result.metadata)
            documents.append(doc)

        return documents

    def similarity_search_with_score(
        self, query: str, k: int = 4, **kwargs: Any
    ) -> list[tuple[Document, float]]:
        """Search with scores (LangChain compatible).

        Args:
            query: Query text
            k: Number of results
            **kwargs: Additional arguments

        Returns:
            List of (document, score) tuples
        """
        # Embed query
        query_embedding = self.embedder.embed(query)

        # Search
        results = self.vector_store.search(query_embedding.numpy, k=k)

        # Convert to documents with scores
        doc_scores = []
        for result in results:
            doc = Document(page_content=result.metadata.get("text", ""), metadata=result.metadata)
            doc_scores.append((doc, result.score))

        return doc_scores

    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> list[Document]:
        """MMR search (LangChain compatible).

        This is a stub for MMR (Maximum Marginal Relevance) search.
        Full implementation would balance relevance and diversity.

        Args:
            query: Query text
            k: Number of results to return
            fetch_k: Number of results to fetch before MMR
            lambda_mult: Balance between relevance (1) and diversity (0)
            **kwargs: Additional arguments

        Returns:
            List of diverse relevant documents
        """
        # For now, just do regular similarity search
        # Full MMR implementation would rerank for diversity
        return self.similarity_search(query, k=fetch_k)[:k]

    @classmethod
    def from_texts(
        cls, texts: list[str], embedding, metadatas: list[dict[str, Any]] | None = None, **kwargs
    ):
        """Create vector store from texts (LangChain compatible).

        Args:
            texts: List of texts
            embedding: Embedding function
            metadatas: Optional metadata
            **kwargs: Additional arguments

        Returns:
            VectorStore instance
        """
        # This would create a new instance and add texts
        # Implementation depends on specific requirements

    def as_retriever(self, **kwargs) -> "BaseRetrieverAdapter":
        """Convert to retriever (LangChain compatible).

        Args:
            **kwargs: Retriever configuration

        Returns:
            Retriever adapter
        """
        return BaseRetrieverAdapter(self, **kwargs)


class BaseRetrieverAdapter(ABC):
    """Adapter to make our retriever compatible with LangChain's BaseRetriever interface."""

    def __init__(self, vector_store_adapter: Any, **kwargs: Any) -> None:
        """Initialize retriever adapter.

        Args:
            vector_store_adapter: VectorStore adapter
            **kwargs: Configuration like k, search_type, etc.
        """
        self.vector_store = vector_store_adapter
        self.search_kwargs = kwargs

    def get_relevant_documents(self, query: str) -> list[Document]:
        """Get relevant documents (LangChain compatible).

        Args:
            query: Query text

        Returns:
            List of relevant documents
        """
        k = self.search_kwargs.get("k", 4)
        search_type = self.search_kwargs.get("search_type", "similarity")

        if search_type == "similarity":
            return self.vector_store.similarity_search(query, k=k)
        if search_type == "mmr":
            fetch_k = self.search_kwargs.get("fetch_k", 20)
            lambda_mult = self.search_kwargs.get("lambda_mult", 0.5)
            return self.vector_store.max_marginal_relevance_search(
                query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult
            )
        raise ValueError(f"Unknown search type: {search_type}")

    async def aget_relevant_documents(self, query: str) -> list[Document]:
        """Async get relevant documents (LangChain compatible).

        Args:
            query: Query text

        Returns:
            List of relevant documents
        """
        # For now, just call sync version
        # Full async implementation would use async methods throughout
        return self.get_relevant_documents(query)


class ChainAdapter:
    """Adapter to make our pipeline compatible with LangChain's Chain interface."""

    def __init__(self, pipeline):
        """Initialize with our RAG pipeline.

        Args:
            pipeline: Our RAGPipeline instance
        """
        self.pipeline = pipeline

    def __call__(self, inputs: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Call the chain (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Returns:
            Output dictionary
        """
        return self.invoke(inputs, **kwargs)

    def invoke(self, inputs: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Invoke the chain (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Returns:
            Output dictionary
        """
        return self.pipeline.invoke(inputs, **kwargs)

    async def ainvoke(self, inputs: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Async invoke the chain (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Returns:
            Output dictionary
        """
        return await self.pipeline.ainvoke(inputs, **kwargs)

    def batch(self, inputs: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """Process batch of inputs (LangChain compatible).

        Args:
            inputs: List of input dictionaries
            **kwargs: Additional arguments

        Returns:
            List of output dictionaries
        """
        return [self.invoke(inp, **kwargs) for inp in inputs]

    def stream(self, inputs: dict[str, Any], **kwargs: Any) -> Any:
        """Stream results (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Yields:
            Streaming results
        """
        # This would implement streaming
        # For now, just return final result
        yield self.invoke(inputs, **kwargs)
