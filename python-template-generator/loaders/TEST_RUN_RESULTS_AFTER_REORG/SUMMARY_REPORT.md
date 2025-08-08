# RAG Framework Test Results

**Test Date:** 2025-08-09T01:18:45.028209

## Configuration

- **chunker:** SemanticChunker
- **max_tokens:** 200
- **overlap_tokens:** 50
- **embedding_model:** all-MiniLM-L6-v2
- **vector_dimensions:** 384
- **vector_store:** FAISS

## Statistics

- **Files Processed:** 249
- **Total Chunks:** 3728
- **Total Vectors:** 3728
- **Avg Processing Time:** 0.177s
- **Total Processing Time:** 44.07s

## Analysis

### Coverage
- **files_indexed:** 249
- **total_chunks:** 3728
- **avg_chunks_per_file:** 14.97
- **total_vectors:** 3728

### Performance
- **avg_query_time:** 0.0050s
- **max_query_time:** 0.0055s
- **min_query_time:** 0.0046s
- **total_indexing_time:** 44.0739s

### Quality
- **avg_relevance_score:** 0.515
- **max_relevance_score:** 0.590
- **min_relevance_score:** 0.450
- **queries_with_results:** 15
- **total_queries:** 15

## Top Performing Queries

1. **Explain semantic chunking**
   - Top Score: 0.590
   - Source: python-template-generator/loaders/API_REFERENCE.md

2. **How to write good documentation?**
   - Top Score: 0.586
   - Source: python-template-generator/CLAUDE.md

3. **What is the git workflow?**
   - Top Score: 0.578
   - Source: python-template-generator/PTOOL/docs/development/git-strategy.md

4. **What embedding models are supported?**
   - Top Score: 0.565
   - Source: python-template-generator/PRPs/semantic_enhancement_INITIAL.md

5. **How does the RAG pipeline work?**
   - Top Score: 0.552
   - Source: python-template-generator/PRPs/cot_semantic_enhancement_PRP.md

