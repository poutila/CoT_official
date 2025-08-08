# RAG Framework Test Results

**Test Date:** 2025-08-09T00:24:22.666450

## Configuration

- **chunker:** SemanticChunker
- **max_tokens:** 200
- **overlap_tokens:** 50
- **embedding_model:** all-MiniLM-L6-v2
- **vector_dimensions:** 384
- **vector_store:** FAISS

## Statistics

- **Files Processed:** 248
- **Total Chunks:** 3690
- **Total Vectors:** 3690
- **Avg Processing Time:** 0.173s
- **Total Processing Time:** 42.87s

## Analysis

### Coverage
- **files_indexed:** 248
- **total_chunks:** 3690
- **avg_chunks_per_file:** 14.88
- **total_vectors:** 3690

### Performance
- **avg_query_time:** 0.0050s
- **max_query_time:** 0.0054s
- **min_query_time:** 0.0047s
- **total_indexing_time:** 42.8719s

### Quality
- **avg_relevance_score:** 0.514
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

