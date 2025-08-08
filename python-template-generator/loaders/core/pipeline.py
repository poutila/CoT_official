"""RAG Pipeline orchestration with LangChain-compatible interfaces."""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any

from chunker import ChunkingConfig, SemanticChunker

# Import our custom components
from enrichers.context_fixed import ContextFixedEnricher
from embeddings import EmbeddingProviderConfig, SentenceTransformerProvider
from .models import (
    Document,
    IndexingResult,
    RAGConfig,
    RetrievalResult,
)
from vector_store import DistanceMetric, FAISSVectorStore, VectorStoreConfig

# Set up logging
logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG Pipeline with LangChain-compatible interfaces.

    This pipeline orchestrates document loading, chunking, embedding,
    storage, and retrieval. It's designed to be compatible with
    LangChain's patterns while using our custom optimized components.
    """

    def __init__(self, config: RAGConfig | None = None):
        """Initialize the RAG pipeline.

        Args:
            config: RAG configuration
        """
        self.config = config or RAGConfig()

        # Initialize components
        self.document_loader = self._init_loader()
        self.text_splitter = self._init_splitter()
        self.embeddings = self._init_embeddings()
        self.vectorstore = self._init_vectorstore()
        self.retriever = self._init_retriever()

        # State
        self.is_indexed = False
        self.indexed_documents = []

        if self.config.verbose:
            logger.info(f"RAG Pipeline initialized with config: {self.config}")

    def _init_loader(self):
        """Initialize document loader.

        Returns our enricher but could return LangChain loader.
        """
        if self.config.loader_type == "markdown":
            return ContextFixedEnricher
        # Could add other loaders here
        return ContextFixedEnricher

    def _init_splitter(self):
        """Initialize text splitter.

        Returns our chunker but could return LangChain splitter.
        """
        config = ChunkingConfig(
            max_tokens=self.config.chunk_size,
            overlap_tokens=self.config.chunk_overlap,
            respect_sentence_boundaries=True,
            respect_paragraph_boundaries=True,
            preserve_code_blocks=True,
        )
        return SemanticChunker(config)

    def _init_embeddings(self):
        """Initialize embeddings.

        Returns our embedder but could return LangChain embeddings.
        """
        config = EmbeddingProviderConfig(
            model_name=self.config.embedding_model,
            device=self.config.embedding_device,
            cache_embeddings=self.config.cache_embeddings,
            batch_size=32,
        )
        return SentenceTransformerProvider(config)

    def _init_vectorstore(self):
        """Initialize vector store.

        Returns our store but could return LangChain vectorstore.
        """
        # Map distance metric
        metric_map = {
            "cosine": DistanceMetric.COSINE,
            "l2": DistanceMetric.L2,
            "euclidean": DistanceMetric.L2,
        }

        config = VectorStoreConfig(
            dimension=self.config.embedding_dimension,
            distance_metric=metric_map.get(self.config.distance_metric, DistanceMetric.COSINE),
            index_type=self.config.index_type,
            persist_directory=self.config.persist_directory,
        )
        return FAISSVectorStore(config)

    def _init_retriever(self):
        """Initialize retriever.

        Returns our custom retriever.
        """
        return CustomRetriever(
            vectorstore=self.vectorstore,
            embeddings=self.embeddings,
            k=self.config.k,
            search_type=self.config.search_type,
            score_threshold=self.config.score_threshold,
        )

    def load_documents(self, paths: Path | list[Path]) -> list[Document]:
        """Load documents from paths.

        Args:
            paths: Path or list of paths to documents

        Returns:
            List of loaded documents
        """
        if isinstance(paths, Path):
            paths = [paths]

        documents = []

        for path in paths:
            if self.config.verbose:
                logger.info(f"Loading document: {path}")

            try:
                # Use our enricher
                enricher = self.document_loader(path)
                doc = enricher.extract_rich_doc()

                # Convert sections to documents
                for section in doc.sections:
                    document = Document(
                        page_content=section.content,
                        metadata={
                            "source": str(path),
                            "section_title": section.title,
                            "section_level": section.level,
                            "section_slug": section.slug,
                        },
                    )
                    documents.append(document)

            except Exception as e:
                logger.error(f"Error loading {path}: {e}")
                if self.config.verbose:
                    raise

        return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split documents into chunks.

        Args:
            documents: List of documents to split

        Returns:
            List of chunked documents
        """
        all_chunks = []

        for doc in documents:
            # Chunk the document
            chunks = self.text_splitter.chunk_text(
                doc.page_content, source_file=doc.metadata.get("source", "unknown")
            )

            # Convert chunks to documents
            for chunk in chunks:
                chunk_doc = Document(
                    page_content=chunk.content,
                    metadata={
                        **doc.metadata,  # Preserve original metadata
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.metadata.chunk_index
                        if hasattr(chunk.metadata, "chunk_index")
                        else 0,
                        "token_count": chunk.token_count,
                        "chunk_type": chunk.chunk_type.value
                        if hasattr(chunk, "chunk_type")
                        else "text",
                    },
                )
                all_chunks.append(chunk_doc)

        return all_chunks

    def index_documents(
        self,
        documents: list[Document] | None = None,
        paths: Path | list[Path] | None = None,
    ) -> IndexingResult:
        """Index documents into the vector store.

        Args:
            documents: Pre-loaded documents to index
            paths: Paths to load and index

        Returns:
            Indexing result with statistics
        """
        start_time = time.time()
        errors = []

        # Load documents if paths provided
        if paths:
            documents = self.load_documents(paths)

        if not documents:
            return IndexingResult(
                total_documents=0,
                total_chunks=0,
                total_embeddings=0,
                time_elapsed=0,
                errors=["No documents to index"],
            )

        total_docs = len(documents)

        if self.config.verbose:
            logger.info(f"Indexing {total_docs} documents...")

        try:
            # Split documents
            chunks = self.split_documents(documents)
            total_chunks = len(chunks)

            if self.config.verbose:
                logger.info(f"Created {total_chunks} chunks")

            # Generate embeddings
            texts = [chunk.page_content for chunk in chunks]
            embeddings_batch = self.embeddings.embed_batch(texts, show_progress=self.config.verbose)

            # Prepare metadata
            metadata_list = [chunk.metadata for chunk in chunks]

            # Add to vector store
            vectors = [emb.numpy for emb in embeddings_batch.embeddings]
            ids = self.vectorstore.add_batch(vectors, metadata_list)

            # Store indexed documents
            self.indexed_documents.extend(chunks)
            self.is_indexed = True

            if self.config.verbose:
                logger.info(f"Indexed {len(ids)} chunks successfully")

            # Save if persist directory is set
            if self.config.persist_directory:
                self.vectorstore.save(self.config.persist_directory)
                if self.config.verbose:
                    logger.info(f"Saved index to {self.config.persist_directory}")

            total_embeddings = len(ids)

        except Exception as e:
            logger.error(f"Error during indexing: {e}")
            errors.append(str(e))
            total_chunks = 0
            total_embeddings = 0

        time_elapsed = time.time() - start_time

        return IndexingResult(
            total_documents=total_docs,
            total_chunks=total_chunks,
            total_embeddings=total_embeddings,
            time_elapsed=time_elapsed,
            errors=errors,
            metadata={
                "chunk_size": self.config.chunk_size,
                "embedding_model": self.config.embedding_model,
                "vector_store_size": self.vectorstore.size,
            },
        )

    def retrieve(
        self, query: str, k: int | None = None, filter_metadata: dict[str, Any] | None = None
    ) -> RetrievalResult:
        """Retrieve relevant documents for a query.

        Args:
            query: Query text
            k: Number of documents to retrieve (overrides config)
            filter_metadata: Metadata filters for retrieval

        Returns:
            Retrieval result with documents and scores
        """
        if not self.is_indexed:
            return RetrievalResult(
                query=query, documents=[], scores=[], metadata={"error": "No documents indexed"}
            )

        k = k or self.config.k

        # Use retriever
        documents, scores = self.retriever.get_relevant_documents_with_scores(
            query, k=k, filter_metadata=filter_metadata
        )

        return RetrievalResult(
            query=query,
            documents=documents,
            scores=scores,
            metadata={
                "k": k,
                "search_type": self.config.search_type,
                "total_indexed": self.vectorstore.size,
            },
        )

    def invoke(self, inputs: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Invoke the pipeline (LangChain compatible).

        Args:
            inputs: Input dictionary with 'query' or 'question' key
            **kwargs: Additional arguments

        Returns:
            Output dictionary with results
        """
        # Extract query
        query = inputs.get("query") or inputs.get("question")
        if not query:
            raise ValueError("Input must contain 'query' or 'question' key")

        # Retrieve documents
        k = kwargs.get("k", self.config.k)
        retrieval_result = self.retrieve(query, k=k)

        # Build response
        response = {
            "query": query,
            "source_documents": retrieval_result.documents,
            "context": retrieval_result.context,
            "metadata": retrieval_result.metadata,
        }

        # Add answer if LLM is configured (future enhancement)
        if kwargs.get("include_answer", False):
            # This would call an LLM with the context
            # For now, just return a placeholder
            response["answer"] = f"Based on {len(retrieval_result.documents)} documents found."

        return response

    async def ainvoke(self, inputs: dict[str, Any], **kwargs) -> dict[str, Any]:
        """Async invoke the pipeline (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Returns:
            Output dictionary
        """
        # For now, just wrap sync version
        # Full async implementation would use async methods throughout
        return await asyncio.get_event_loop().run_in_executor(None, self.invoke, inputs, kwargs)

    def stream(self, inputs: dict[str, Any], **kwargs):
        """Stream results (LangChain compatible).

        Args:
            inputs: Input dictionary
            **kwargs: Additional arguments

        Yields:
            Streaming results
        """
        # Simple streaming implementation
        # Full implementation would stream from LLM
        result = self.invoke(inputs, **kwargs)

        # Stream documents one by one
        for doc in result.get("source_documents", []):
            yield {"document": doc}

        # Final result
        yield {"final": result}

    def batch(self, inputs_list: list[dict[str, Any]], **kwargs) -> list[dict[str, Any]]:
        """Process batch of inputs.

        Args:
            inputs_list: List of input dictionaries
            **kwargs: Additional arguments

        Returns:
            List of output dictionaries
        """
        return [self.invoke(inputs, **kwargs) for inputs in inputs_list]

    def save(self, path: str | Path) -> None:
        """Save the pipeline state.

        Args:
            path: Path to save the pipeline
        """
        path = Path(path)
        self.vectorstore.save(path / "vectorstore")

        # Could save config and other state here

        if self.config.verbose:
            logger.info(f"Pipeline saved to {path}")

    def load(self, path: str | Path) -> None:
        """Load the pipeline state.

        Args:
            path: Path to load the pipeline from
        """
        path = Path(path)
        self.vectorstore.load(path / "vectorstore")
        self.is_indexed = True

        if self.config.verbose:
            logger.info(f"Pipeline loaded from {path}")


class CustomRetriever:
    """Custom retriever that works with our components."""

    def __init__(
        self,
        vectorstore,
        embeddings,
        k: int = 4,
        search_type: str = "similarity",
        score_threshold: float | None = None,
    ):
        """Initialize retriever.

        Args:
            vectorstore: Vector store instance
            embeddings: Embeddings instance
            k: Number of documents to retrieve
            search_type: Type of search
            score_threshold: Minimum score threshold
        """
        self.vectorstore = vectorstore
        self.embeddings = embeddings
        self.k = k
        self.search_type = search_type
        self.score_threshold = score_threshold

    def get_relevant_documents(
        self, query: str, k: int | None = None, filter_metadata: dict[str, Any] | None = None
    ) -> list[Document]:
        """Get relevant documents.

        Args:
            query: Query text
            k: Number of documents
            filter_metadata: Metadata filters

        Returns:
            List of relevant documents
        """
        documents, _ = self.get_relevant_documents_with_scores(
            query, k=k, filter_metadata=filter_metadata
        )
        return documents

    def get_relevant_documents_with_scores(
        self, query: str, k: int | None = None, filter_metadata: dict[str, Any] | None = None
    ) -> tuple[list[Document], list[float]]:
        """Get relevant documents with scores.

        Args:
            query: Query text
            k: Number of documents
            filter_metadata: Metadata filters

        Returns:
            Tuple of (documents, scores)
        """
        k = k or self.k

        # Embed query
        query_embedding = self.embeddings.embed(query)

        # Search
        results = self.vectorstore.search(
            query_embedding.numpy, k=k, filter_metadata=filter_metadata, include_vectors=False
        )

        # Filter by score threshold if set
        if self.score_threshold:
            results = [r for r in results if r.score >= self.score_threshold]

        # Convert to documents
        documents = []
        scores = []

        for result in results:
            # Get content from metadata
            content = result.metadata.get("text", result.metadata.get("content", ""))

            doc = Document(page_content=content, metadata=result.metadata)
            documents.append(doc)
            scores.append(result.score)

        return documents, scores

    async def aget_relevant_documents(self, query: str, k: int | None = None) -> list[Document]:
        """Async get relevant documents.

        Args:
            query: Query text
            k: Number of documents

        Returns:
            List of relevant documents
        """
        # For now, wrap sync version
        return await asyncio.get_event_loop().run_in_executor(
            None, self.get_relevant_documents, query, k
        )
