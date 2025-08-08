"""Integration tests for RAG pipeline."""

import pytest
from core.models import Document, RAGConfig
from core.pipeline import RAGPipeline


@pytest.mark.integration
class TestRAGPipelineIntegration:
    """Integration tests for complete RAG pipeline."""

    def test_end_to_end_pipeline(self, temp_dir):
        """Test complete pipeline from indexing to retrieval."""
        # Create pipeline
        config = RAGConfig(
            chunk_size=100, chunk_overlap=10, embedding_model="all-MiniLM-L6-v2", k=2, verbose=False
        )
        pipeline = RAGPipeline(config)

        # Create test documents
        docs = [
            Document(
                page_content="Python is a versatile programming language.",
                metadata={"source": "doc1.md", "topic": "python"},
            ),
            Document(
                page_content="Machine learning uses statistical methods.",
                metadata={"source": "doc2.md", "topic": "ml"},
            ),
            Document(
                page_content="Data science combines multiple disciplines.",
                metadata={"source": "doc3.md", "topic": "ds"},
            ),
        ]

        # Index documents
        result = pipeline.index_documents(documents=docs)
        assert result.total_documents == 3
        assert result.total_chunks >= 3
        assert result.total_embeddings >= 3
        assert len(result.errors) == 0

        # Test retrieval
        query_result = pipeline.retrieve("Python programming", k=2)
        assert len(query_result.documents) == 2
        assert len(query_result.scores) == 2
        assert query_result.scores[0] >= query_result.scores[1]  # Ordered by score

    def test_pipeline_persistence(self, temp_dir):
        """Test saving and loading pipeline state."""
        # Create and populate pipeline
        config = RAGConfig(chunk_size=100, verbose=False)
        pipeline1 = RAGPipeline(config)

        docs = [Document(page_content="Test document for persistence.", metadata={"id": "test1"})]
        pipeline1.index_documents(documents=docs)

        # Save pipeline
        save_path = temp_dir / "test_pipeline"
        pipeline1.save(save_path)
        assert save_path.exists()

        # Load in new pipeline
        pipeline2 = RAGPipeline(config)
        pipeline2.load(save_path)

        # Verify loaded pipeline works
        result = pipeline2.retrieve("test document", k=1)
        assert len(result.documents) == 1
        assert result.documents[0].metadata["id"] == "test1"

    def test_pipeline_with_markdown_files(self, sample_markdown_file):
        """Test pipeline with actual markdown files."""
        config = RAGConfig(chunk_size=50, chunk_overlap=10, verbose=False)
        pipeline = RAGPipeline(config)

        # Index markdown file
        result = pipeline.index_documents(paths=[sample_markdown_file])
        assert result.total_documents > 0
        assert result.total_chunks > 0

        # Search for content
        query_result = pipeline.retrieve("code block", k=2)
        assert len(query_result.documents) > 0

    def test_pipeline_batch_processing(self):
        """Test batch query processing."""
        config = RAGConfig(verbose=False)
        pipeline = RAGPipeline(config)

        # Index documents
        docs = [
            Document(page_content=f"Document {i}: Content about topic {i % 3}") for i in range(10)
        ]
        pipeline.index_documents(documents=docs)

        # Batch queries
        queries = [{"query": "topic 0"}, {"query": "topic 1"}, {"query": "topic 2"}]

        results = pipeline.batch(queries)
        assert len(results) == 3
        for result in results:
            assert "source_documents" in result
            assert "context" in result

    def test_pipeline_invoke_interface(self):
        """Test LangChain-compatible invoke interface."""
        pipeline = RAGPipeline()

        # Index sample data
        docs = [Document(page_content="LangChain compatible interface test.")]
        pipeline.index_documents(documents=docs)

        # Test invoke
        result = pipeline.invoke({"query": "interface test"})
        assert "query" in result
        assert "source_documents" in result
        assert "context" in result
        assert "metadata" in result

    def test_pipeline_streaming(self):
        """Test streaming interface."""
        pipeline = RAGPipeline()

        docs = [Document(page_content=f"Stream document {i}") for i in range(3)]
        pipeline.index_documents(documents=docs)

        # Test streaming
        stream_results = list(pipeline.stream({"query": "stream"}))
        assert len(stream_results) > 0

        # Should have document chunks and final result
        has_docs = any("document" in r for r in stream_results)
        has_final = any("final" in r for r in stream_results)
        assert has_docs or has_final

    def test_pipeline_with_filters(self):
        """Test retrieval with metadata filters."""
        pipeline = RAGPipeline()

        # Index documents with different categories
        docs = [
            Document(
                page_content="Python programming guide",
                metadata={"category": "programming", "level": "beginner"},
            ),
            Document(
                page_content="Python data science",
                metadata={"category": "data", "level": "intermediate"},
            ),
            Document(
                page_content="Python web development",
                metadata={"category": "web", "level": "beginner"},
            ),
        ]
        pipeline.index_documents(documents=docs)

        # Search with filter
        result = pipeline.retrieve("Python", k=2, filter_metadata={"category": "programming"})

        # Should only return matching category
        for doc in result.documents:
            assert doc.metadata.get("category") == "programming"

    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        pipeline = RAGPipeline()

        # Query without indexing
        result = pipeline.retrieve("test query")
        assert len(result.documents) == 0
        assert "error" in result.metadata

        # Invalid invoke input
        with pytest.raises(ValueError):
            pipeline.invoke({"invalid_key": "test"})

        # Empty document indexing
        result = pipeline.index_documents(documents=[])
        assert result.total_documents == 0
        assert len(result.errors) > 0

    @pytest.mark.slow
    def test_pipeline_performance(self):
        """Test pipeline performance with larger dataset."""
        import time

        pipeline = RAGPipeline(RAGConfig(verbose=False))

        # Create larger dataset
        docs = [
            Document(
                page_content=f"Document {i}: " + "content " * 50,
                metadata={"id": i, "batch": i // 10},
            )
            for i in range(100)
        ]

        # Measure indexing time
        start = time.time()
        result = pipeline.index_documents(documents=docs)
        index_time = time.time() - start

        assert result.total_documents == 100
        assert index_time < 10  # Should complete within 10 seconds

        # Measure query time
        start = time.time()
        query_result = pipeline.retrieve("document content", k=10)
        query_time = time.time() - start

        assert len(query_result.documents) == 10
        assert query_time < 1  # Query should be fast
