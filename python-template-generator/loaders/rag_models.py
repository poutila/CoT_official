"""Models for RAG pipeline with LangChain compatibility."""

from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime


class Document(BaseModel):
    """Document model compatible with LangChain's Document.
    
    This model is designed to be compatible with LangChain's Document
    schema while working with our custom components.
    """
    
    page_content: str = Field(
        description="The main content of the document"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the document"
    )
    
    @property
    def content(self) -> str:
        """Alias for page_content for backward compatibility."""
        return self.page_content
    
    def __str__(self) -> str:
        """String representation."""
        preview = self.page_content[:100] + "..." if len(self.page_content) > 100 else self.page_content
        return f"Document(content='{preview}', metadata={list(self.metadata.keys())})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "page_content": self.page_content,
            "metadata": self.metadata
        }


class RAGConfig(BaseModel):
    """Configuration for RAG pipeline compatible with LangChain parameters."""
    
    model_config = {"protected_namespaces": ()}
    
    # Document loading
    loader_type: str = Field(
        default="markdown",
        description="Type of document loader"
    )
    
    # Chunking parameters (maps to LangChain's TextSplitter)
    chunk_size: int = Field(
        default=512,
        description="Maximum size of chunks (in tokens)"
    )
    chunk_overlap: int = Field(
        default=50,
        description="Overlap between chunks (in tokens)"
    )
    separators: Optional[List[str]] = Field(
        default=None,
        description="Separators for splitting (like LangChain's separators)"
    )
    
    # Embedding parameters
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="Name of the embedding model"
    )
    embedding_dimension: int = Field(
        default=384,
        description="Dimension of embeddings"
    )
    embedding_device: str = Field(
        default="cpu",
        description="Device for embeddings (cpu/cuda)"
    )
    
    # Vector store parameters
    vector_store_type: str = Field(
        default="faiss",
        description="Type of vector store"
    )
    distance_metric: str = Field(
        default="cosine",
        description="Distance metric for similarity"
    )
    index_type: str = Field(
        default="Flat",
        description="Index type for vector store"
    )
    persist_directory: Optional[Path] = Field(
        default=None,
        description="Directory to persist the vector store"
    )
    
    # Retrieval parameters (maps to LangChain's retriever)
    k: int = Field(
        default=4,
        description="Number of documents to retrieve"
    )
    search_type: str = Field(
        default="similarity",
        description="Type of search (similarity, mmr, threshold)"
    )
    score_threshold: Optional[float] = Field(
        default=None,
        description="Minimum similarity score threshold"
    )
    fetch_k: int = Field(
        default=20,
        description="Number of documents to fetch before filtering (for MMR)"
    )
    lambda_mult: float = Field(
        default=0.5,
        description="Lambda for MMR (0=max diversity, 1=max relevance)"
    )
    
    # Pipeline parameters
    verbose: bool = Field(
        default=False,
        description="Whether to print verbose output"
    )
    return_source_documents: bool = Field(
        default=True,
        description="Whether to return source documents with results"
    )
    max_tokens_limit: Optional[int] = Field(
        default=2000,
        description="Maximum tokens for context window"
    )
    
    # Cache parameters
    cache_embeddings: bool = Field(
        default=True,
        description="Whether to cache embeddings"
    )
    cache_size: int = Field(
        default=1000,
        description="Maximum cache size"
    )


class RetrievalResult(BaseModel):
    """Result from retrieval operation."""
    
    query: str = Field(
        description="Original query"
    )
    documents: List[Document] = Field(
        description="Retrieved documents"
    )
    scores: Optional[List[float]] = Field(
        default=None,
        description="Similarity scores for each document"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the retrieval"
    )
    
    @property
    def context(self) -> str:
        """Get concatenated context from all documents."""
        return "\n\n".join(doc.page_content for doc in self.documents)
    
    @property
    def source_documents(self) -> List[Document]:
        """Alias for documents (LangChain compatibility)."""
        return self.documents


class IndexingResult(BaseModel):
    """Result from document indexing."""
    
    total_documents: int = Field(
        description="Total number of documents processed"
    )
    total_chunks: int = Field(
        description="Total number of chunks created"
    )
    total_embeddings: int = Field(
        description="Total number of embeddings generated"
    )
    time_elapsed: float = Field(
        description="Time taken in seconds"
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Any errors encountered"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class RAGResponse(BaseModel):
    """Response from RAG pipeline (LangChain compatible structure)."""
    
    answer: Optional[str] = Field(
        default=None,
        description="Generated answer (if using LLM)"
    )
    source_documents: List[Document] = Field(
        default_factory=list,
        description="Source documents used"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @property
    def result(self) -> Optional[str]:
        """Alias for answer (LangChain compatibility)."""
        return self.answer
    
    @property
    def sources(self) -> List[str]:
        """Get source references."""
        sources = []
        for doc in self.source_documents:
            if "source" in doc.metadata:
                sources.append(doc.metadata["source"])
            elif "file_path" in doc.metadata:
                sources.append(doc.metadata["file_path"])
        return list(set(sources))  # Unique sources


class ChainType(str, Enum):
    """Types of chains (for future LangChain compatibility)."""
    STUFF = "stuff"  # Pass all documents to LLM
    MAP_REDUCE = "map_reduce"  # Summarize each doc, then combine
    REFINE = "refine"  # Iteratively refine answer
    MAP_RERANK = "map_rerank"  # Score each doc and use best


class PromptTemplate(BaseModel):
    """Prompt template compatible with LangChain."""
    
    template: str = Field(
        description="Template string with {variables}"
    )
    input_variables: List[str] = Field(
        description="List of input variable names"
    )
    template_format: str = Field(
        default="f-string",
        description="Format of the template"
    )
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        # Check all required variables are provided
        missing = set(self.input_variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        return self.template.format(**kwargs)
    
    def partial(self, **kwargs) -> 'PromptTemplate':
        """Create a partial prompt template."""
        new_template = self.template
        new_variables = self.input_variables.copy()
        
        for key, value in kwargs.items():
            if key in new_variables:
                new_template = new_template.replace(f"{{{key}}}", str(value))
                new_variables.remove(key)
        
        return PromptTemplate(
            template=new_template,
            input_variables=new_variables,
            template_format=self.template_format
        )


# Default prompt templates
DEFAULT_QA_PROMPT = PromptTemplate(
    template="""Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer:""",
    input_variables=["context", "question"]
)

DEFAULT_SUMMARIZE_PROMPT = PromptTemplate(
    template="""Summarize the following text concisely:

{text}

Summary:""",
    input_variables=["text"]
)