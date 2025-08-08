#!/usr/bin/env python3
"""
Test RAG Framework on Markdown Documentation

This script tests the complete RAG pipeline on all markdown files in the project,
saving detailed results for analysis.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import numpy as np

# Force CPU mode for consistent testing
os.environ['CUDA_VISIBLE_DEVICES'] = ''

# Add parent directory to path (loaders/)
sys.path.insert(0, str(Path(__file__).parent.parent))

from chunker import SemanticChunker
from chunker.models import ChunkingConfig
from embeddings import SentenceTransformerProvider
from embeddings.models import EmbeddingProviderConfig
from vector_store import FAISSVectorStore
from vector_store.models import VectorStoreConfig


class MarkdownRAGTester:
    """Test RAG framework on markdown documentation."""
    
    def __init__(self, output_dir: Path):
        """Initialize tester with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        print("Initializing RAG components...")
        self.chunker = SemanticChunker(
            ChunkingConfig(max_tokens=200, overlap_tokens=50)
        )
        self.embedder = SentenceTransformerProvider(
            EmbeddingProviderConfig(model_name='all-MiniLM-L6-v2', device='cpu')
        )
        self.store = FAISSVectorStore(
            VectorStoreConfig(dimensions=384)
        )
        
        # Results tracking
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'chunker': 'SemanticChunker',
                'max_tokens': 200,
                'overlap_tokens': 50,
                'embedding_model': 'all-MiniLM-L6-v2',
                'vector_dimensions': 384,
                'vector_store': 'FAISS'
            },
            'files_processed': [],
            'statistics': {},
            'queries_tested': [],
            'errors': []
        }
    
    def process_markdown_files(self, md_files: List[Path]) -> Dict[str, Any]:
        """Process all markdown files and build index."""
        print(f"\nProcessing {len(md_files)} markdown files...")
        
        total_chunks = 0
        total_tokens = 0
        processing_times = []
        
        for i, file_path in enumerate(md_files, 1):
            print(f"  [{i}/{len(md_files)}] Processing {file_path.name}...")
            start_time = time.time()
            
            try:
                # Read file
                content = file_path.read_text(encoding='utf-8')
                
                # Chunk the content
                # Get project root (CoT_official)
                project_root = Path(__file__).parent.parent.parent.parent
                relative_path = file_path.relative_to(project_root)
                chunks = self.chunker.chunk_text(
                    content, 
                    source_file=str(relative_path)
                )
                
                # Process each chunk
                file_chunks = 0
                for chunk in chunks:
                    # Generate embedding
                    embedding = self.embedder.embed(chunk.content)
                    vec = np.array(embedding.embedding) if not isinstance(
                        embedding.embedding, np.ndarray
                    ) else embedding.embedding
                    
                    # Store with metadata
                    metadata = {
                        'text': chunk.content,
                        'source': str(relative_path),
                        'chunk_id': chunk.chunk_id,
                        'chunk_type': str(chunk.chunk_type),
                        'file_name': file_path.name
                    }
                    self.store.add(vec, metadata)
                    file_chunks += 1
                
                processing_time = time.time() - start_time
                processing_times.append(processing_time)
                
                # Track results
                self.results['files_processed'].append({
                    'file': str(relative_path),
                    'size_bytes': len(content.encode('utf-8')),
                    'chunks_created': file_chunks,
                    'processing_time': processing_time
                })
                
                total_chunks += file_chunks
                print(f"    ✓ Created {file_chunks} chunks in {processing_time:.2f}s")
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                print(f"    ✗ {error_msg}")
                self.results['errors'].append(error_msg)
        
        # Calculate statistics
        self.results['statistics'] = {
            'total_files': len(md_files),
            'successful_files': len(self.results['files_processed']),
            'total_chunks': total_chunks,
            'total_vectors': self.store.size,
            'avg_processing_time': np.mean(processing_times) if processing_times else 0,
            'total_processing_time': sum(processing_times)
        }
        
        return self.results['statistics']
    
    def test_queries(self) -> List[Dict[str, Any]]:
        """Test various queries against the index."""
        print("\nTesting queries...")
        
        # Define test queries covering different topics
        test_queries = [
            # Architecture queries
            "What is the architecture of the system?",
            "How does the RAG pipeline work?",
            "Explain the chunking strategy",
            
            # Code quality queries
            "What are the testing standards?",
            "How to ensure code quality?",
            "What are the security requirements?",
            
            # Development queries
            "How to set up the development environment?",
            "What is the git workflow?",
            "How to contribute to the project?",
            
            # Specific component queries
            "How does the vector store work?",
            "What embedding models are supported?",
            "Explain semantic chunking",
            
            # Documentation queries
            "What documentation standards exist?",
            "How to write good documentation?",
            "What is Chain of Thought?",
        ]
        
        query_results = []
        
        for query in test_queries:
            print(f"  Testing: {query}")
            start_time = time.time()
            
            # Generate query embedding
            query_embedding = self.embedder.embed(query)
            query_vec = np.array(query_embedding.embedding) if not isinstance(
                query_embedding.embedding, np.ndarray
            ) else query_embedding.embedding
            
            # Search
            results = self.store.search(query_vec, k=3)
            search_time = time.time() - start_time
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'score': float(result.score),
                    'source': result.metadata.get('source', 'unknown'),
                    'text_preview': result.metadata.get('text', '')[:200],
                    'chunk_type': result.metadata.get('chunk_type', 'unknown')
                })
            
            query_result = {
                'query': query,
                'search_time': search_time,
                'num_results': len(results),
                'results': formatted_results
            }
            
            query_results.append(query_result)
            
            if results:
                print(f"    ✓ Found {len(results)} results (top score: {results[0].score:.3f})")
            else:
                print(f"    ✗ No results found")
        
        self.results['queries_tested'] = query_results
        return query_results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze the test results."""
        print("\nAnalyzing results...")
        
        analysis = {
            'coverage': {},
            'performance': {},
            'quality': {}
        }
        
        # Coverage analysis
        total_files = len(self.results['files_processed'])
        total_chunks = self.results['statistics']['total_chunks']
        
        analysis['coverage'] = {
            'files_indexed': total_files,
            'total_chunks': total_chunks,
            'avg_chunks_per_file': total_chunks / total_files if total_files > 0 else 0,
            'total_vectors': self.results['statistics']['total_vectors']
        }
        
        # Performance analysis
        query_times = [q['search_time'] for q in self.results['queries_tested']]
        analysis['performance'] = {
            'avg_query_time': np.mean(query_times) if query_times else 0,
            'max_query_time': max(query_times) if query_times else 0,
            'min_query_time': min(query_times) if query_times else 0,
            'total_indexing_time': self.results['statistics']['total_processing_time']
        }
        
        # Quality analysis
        all_scores = []
        for query_result in self.results['queries_tested']:
            for result in query_result['results']:
                all_scores.append(result['score'])
        
        analysis['quality'] = {
            'avg_relevance_score': np.mean(all_scores) if all_scores else 0,
            'max_relevance_score': max(all_scores) if all_scores else 0,
            'min_relevance_score': min(all_scores) if all_scores else 0,
            'queries_with_results': sum(1 for q in self.results['queries_tested'] if q['num_results'] > 0),
            'total_queries': len(self.results['queries_tested'])
        }
        
        self.results['analysis'] = analysis
        return analysis
    
    def save_results(self):
        """Save all results to files."""
        print("\nSaving results...")
        
        # Save main results JSON
        results_file = self.output_dir / 'test_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Saved results to {results_file}")
        
        # Save summary report
        self.save_summary_report()
        
        # Save query results in readable format
        self.save_query_results()
        
        # Save vector store for future use
        store_path = self.output_dir / 'vector_store'
        self.store.save(store_path)
        print(f"  ✓ Saved vector store to {store_path}")
    
    def save_summary_report(self):
        """Save human-readable summary report."""
        report_file = self.output_dir / 'SUMMARY_REPORT.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# RAG Framework Test Results\n\n")
            f.write(f"**Test Date:** {self.results['timestamp']}\n\n")
            
            # Configuration
            f.write("## Configuration\n\n")
            for key, value in self.results['configuration'].items():
                f.write(f"- **{key}:** {value}\n")
            
            # Statistics
            f.write("\n## Statistics\n\n")
            stats = self.results['statistics']
            f.write(f"- **Files Processed:** {stats['total_files']}\n")
            f.write(f"- **Total Chunks:** {stats['total_chunks']}\n")
            f.write(f"- **Total Vectors:** {stats['total_vectors']}\n")
            f.write(f"- **Avg Processing Time:** {stats['avg_processing_time']:.3f}s\n")
            f.write(f"- **Total Processing Time:** {stats['total_processing_time']:.2f}s\n")
            
            # Analysis
            if 'analysis' in self.results:
                f.write("\n## Analysis\n\n")
                
                f.write("### Coverage\n")
                for key, value in self.results['analysis']['coverage'].items():
                    f.write(f"- **{key}:** {value:.2f}\n" if isinstance(value, float) else f"- **{key}:** {value}\n")
                
                f.write("\n### Performance\n")
                for key, value in self.results['analysis']['performance'].items():
                    f.write(f"- **{key}:** {value:.4f}s\n")
                
                f.write("\n### Quality\n")
                for key, value in self.results['analysis']['quality'].items():
                    if isinstance(value, float):
                        f.write(f"- **{key}:** {value:.3f}\n")
                    else:
                        f.write(f"- **{key}:** {value}\n")
            
            # Top performing queries
            f.write("\n## Top Performing Queries\n\n")
            sorted_queries = sorted(
                self.results['queries_tested'],
                key=lambda x: x['results'][0]['score'] if x['results'] else 0,
                reverse=True
            )[:5]
            
            for i, query in enumerate(sorted_queries, 1):
                if query['results']:
                    f.write(f"{i}. **{query['query']}**\n")
                    f.write(f"   - Top Score: {query['results'][0]['score']:.3f}\n")
                    f.write(f"   - Source: {query['results'][0]['source']}\n\n")
            
            # Errors
            if self.results['errors']:
                f.write("\n## Errors\n\n")
                for error in self.results['errors']:
                    f.write(f"- {error}\n")
        
        print(f"  ✓ Saved summary report to {report_file}")
    
    def save_query_results(self):
        """Save detailed query results."""
        query_file = self.output_dir / 'query_results.md'
        
        with open(query_file, 'w', encoding='utf-8') as f:
            f.write("# Query Test Results\n\n")
            
            for query_result in self.results['queries_tested']:
                f.write(f"## Query: {query_result['query']}\n\n")
                f.write(f"**Search Time:** {query_result['search_time']:.4f}s\n")
                f.write(f"**Results Found:** {query_result['num_results']}\n\n")
                
                for i, result in enumerate(query_result['results'], 1):
                    f.write(f"### Result {i}\n")
                    f.write(f"- **Score:** {result['score']:.3f}\n")
                    f.write(f"- **Source:** {result['source']}\n")
                    f.write(f"- **Type:** {result['chunk_type']}\n")
                    f.write(f"- **Preview:** {result['text_preview']}...\n\n")
                
                f.write("---\n\n")
        
        print(f"  ✓ Saved query results to {query_file}")


def main():
    """Main test execution."""
    print("=" * 60)
    print("RAG Framework Markdown Documentation Test")
    print("=" * 60)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent  # loaders directory
    output_dir = base_dir / 'TEST_RUN_RESULTS_AFTER_REORG'
    
    # Find all markdown files within the project
    project_root = base_dir.parent.parent  # CoT_official directory
    md_files = []
    
    # Search for markdown files only within the project
    for file in project_root.glob('**/*.md'):
        # Skip unwanted directories
        skip_dirs = ['TEST_RUN_RESULTS', 'node_modules', '.venv', 'venv', '__pycache__', '.git']
        if not any(skip_dir in str(file) for skip_dir in skip_dirs):
            # Only include files that are actually in our project
            try:
                file.relative_to(project_root)
                md_files.append(file)
            except ValueError:
                # File is outside project root, skip it
                continue
    
    # Sort files
    md_files = sorted(md_files)
    
    print(f"\nFound {len(md_files)} markdown files to process")
    
    # Initialize tester
    tester = MarkdownRAGTester(output_dir)
    
    # Process files
    stats = tester.process_markdown_files(md_files)
    print(f"\n✓ Indexed {stats['total_chunks']} chunks from {stats['total_files']} files")
    
    # Test queries
    query_results = tester.test_queries()
    print(f"\n✓ Tested {len(query_results)} queries")
    
    # Analyze results
    analysis = tester.analyze_results()
    print(f"\n✓ Analysis complete:")
    print(f"  - Average relevance score: {analysis['quality']['avg_relevance_score']:.3f}")
    print(f"  - Average query time: {analysis['performance']['avg_query_time']:.4f}s")
    print(f"  - Queries with results: {analysis['quality']['queries_with_results']}/{analysis['quality']['total_queries']}")
    
    # Save all results
    tester.save_results()
    
    print("\n" + "=" * 60)
    print("✅ Test Complete! Results saved to TEST_RUN_RESULTS/")
    print("=" * 60)


if __name__ == "__main__":
    main()