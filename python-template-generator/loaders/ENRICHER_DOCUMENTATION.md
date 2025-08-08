# Markdown Document Enricher Documentation

The `ContextFixedEnricher` is the foundational component that extracts rich semantic information from markdown documents, enabling advanced document understanding and processing.

## 📋 Table of Contents
- [Overview](#overview)
- [Core Features](#core-features)
- [Installation & Setup](#installation--setup)
- [Basic Usage](#basic-usage)
- [Extracted Information](#extracted-information)
- [Advanced Features](#advanced-features)
- [Extension Architecture](#extension-architecture)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

## Overview

The enricher parses markdown documents and extracts structured semantic information, going far beyond simple text extraction to understand document structure, code examples, requirements, and relationships.

### Why Use the Enricher?

Traditional markdown parsers give you raw AST nodes. The enricher gives you:
- **Semantic Understanding**: Knows what's a requirement, example, or definition
- **Hierarchical Structure**: Preserves document organization
- **Code Intelligence**: Detects good/bad examples and patterns
- **Context Preservation**: Maintains relationships between elements
- **Production Ready**: Battle-tested on complex documentation

## Core Features

### 🏗️ Structural Extraction
- **Sections & Hierarchy**: Complete document structure with nested sections
- **Code Blocks**: All code with language detection and metadata
- **Tables**: Structured table data with headers and rows
- **Lists**: Organized lists with nesting levels
- **Links**: Internal and external references

### 🎯 Semantic Extraction
- **Requirements**: Detected requirements with IDs and descriptions
- **Examples**: Good/bad example patterns with classification
- **Definitions**: Term definitions and glossary entries
- **Metadata**: Document metadata and front matter
- **Context**: Surrounding context for code blocks

### 🔍 Pattern Detection
- **Example Classification**: Automatically identifies good/bad/neutral examples
- **Pattern Markers**: Detects ✅ GOOD, ❌ BAD, and other markers
- **Code Patterns**: Recognizes common coding patterns
- **Multi-Example Splitting**: Separates mixed example blocks

## Installation & Setup

### Dependencies
```bash
# Core dependencies (already in pyproject.toml)
uv add markdown-it-py pydantic

# Optional for enhanced features
uv add beautifulsoup4  # For HTML in markdown
uv add python-frontmatter  # For YAML frontmatter
```

### Basic Setup
```python
from context_fixed_enricher import ContextFixedEnricher
from pathlib import Path

# Initialize with a markdown file
enricher = ContextFixedEnricher(Path("document.md"))

# Or with string path
enricher = ContextFixedEnricher("document.md")
```

## Basic Usage

### Simple Extraction
```python
from context_fixed_enricher import ContextFixedEnricher

# Create enricher
enricher = ContextFixedEnricher("README.md")

# Extract rich document
doc = enricher.extract_rich_doc()

# Access basic information
print(f"Title: {doc.title}")
print(f"Sections: {len(doc.sections)}")
print(f"Code blocks: {len(doc.code_blocks)}")
print(f"Requirements: {len(doc.requirements)}")
```

### Accessing Sections
```python
# Iterate through sections
for section in doc.sections:
    print(f"{' ' * (section.level-1)}├── {section.title}")
    print(f"    Content: {len(section.content)} chars")
    print(f"    Code blocks: {len(section.code_blocks)}")
    
    # Access subsections
    for subsection in section.subsections:
        print(f"      └── {subsection.title}")
```

### Working with Code Blocks
```python
# Get all code blocks
for block in doc.code_blocks:
    print(f"Language: {block.language}")
    print(f"Section: {block.section_slug}")
    print(f"Lines: {block.line_start}")
    print(f"Content preview: {block.content[:100]}...")
    
    # Check if it's an example
    if hasattr(block, 'example_type'):
        print(f"Example type: {block.example_type}")
```

## Extracted Information

### Document Model Structure

```python
class MarkdownDocExtendedRich:
    """Complete enriched document model."""
    
    # Basic Info
    title: str                          # Document title
    file_path: str                      # Source file path
    
    # Structural Elements
    sections: List[Section]             # Hierarchical sections
    code_blocks: List[CodeBlock]        # All code blocks
    tables: List[Table]                 # All tables
    lists: List[ListBlock]              # All lists
    links: List[Link]                   # All links
    
    # Semantic Elements
    requirements: List[Requirement]      # Detected requirements
    examples: List[CodeExample]         # Classified examples
    definitions: Dict[str, Definition]  # Term definitions
    
    # Metadata
    metadata: DocumentMetadata           # Document metadata
    stats: DocumentStats                # Statistics
```

### Section Model
```python
class Section:
    """Document section with hierarchy."""
    
    title: str                    # Section heading
    level: int                    # Heading level (1-6)
    slug: str                     # URL-safe identifier
    content: str                  # Section text content
    subsections: List[Section]    # Nested subsections
    
    # Section-specific elements
    code_blocks: List[CodeBlock]  # Code in this section
    requirements: List[str]        # Requirement IDs
    tables: List[Table]           # Tables in section
    
    # Metrics
    word_count: int
    char_count: int
```

### Code Block Model
```python
class CodeBlock:
    """Code block with metadata."""
    
    content: str              # Code content
    language: str            # Programming language
    section_slug: str        # Parent section
    line_start: Optional[int] # Starting line number
    
    # Enhanced properties (if detected)
    is_example: bool         # Is this an example?
    example_type: str        # GOOD/BAD/NEUTRAL
    has_output: bool         # Has output/result?
```

### Code Example Model
```python
class CodeExample:
    """Classified code example with context."""
    
    code: str                      # Example code
    language: str                  # Programming language
    example_type: ExampleType      # Classification
    
    # Context
    context_before: str            # Text before example
    context_after: str             # Text after example
    section_slug: str              # Parent section
    
    # Pattern detection
    patterns_found: List[str]      # Detected patterns
    confidence: float              # Classification confidence
```

### Requirement Model
```python
class Requirement:
    """Detected requirement."""
    
    id: str                   # Requirement ID (REQ-001)
    description: str          # Requirement text
    section_slug: str         # Parent section
    priority: Optional[str]   # HIGH/MEDIUM/LOW
    category: Optional[str]   # Category/type
```

## Advanced Features

### Example Detection & Classification

The enricher automatically detects and classifies code examples:

```python
# Access classified examples
for example in doc.examples:
    if example.example_type == ExampleType.GOOD:
        print(f"✅ Good example in {example.section_slug}")
        print(f"   Context: {example.context_before[:100]}")
        print(f"   Code: {example.code[:100]}")
        
    elif example.example_type == ExampleType.BAD:
        print(f"❌ Bad example: {example.patterns_found}")
```

#### Pattern Detection Markers
The enricher recognizes 30+ patterns including:
- `✅ GOOD`, `✅`, `# Good`, `# Best practice`
- `❌ BAD`, `❌`, `# Bad`, `# Anti-pattern`
- `# DO:`, `# DON'T:`, `# AVOID:`
- Comment-based markers in code

### Multi-Example Block Splitting

Automatically splits code blocks containing multiple examples:

```python
# Original block with mixed examples
"""
# ❌ BAD: Direct print
print("debug info")

# ✅ GOOD: Use logging
logger.debug("debug info")
"""

# Becomes two separate examples:
# 1. BAD example with print
# 2. GOOD example with logger
```

### Context Extraction

Each code block includes surrounding context:

```python
for block in doc.code_blocks:
    # Access context
    example = enricher.find_example_for_block(block)
    if example:
        print(f"Before: {example.context_before}")
        print(f"Code: {example.code}")
        print(f"After: {example.context_after}")
```

### Requirement Detection

Automatically identifies requirements:

```python
# Patterns detected:
# - "MUST", "SHALL", "SHOULD", "REQUIRED"
# - "REQ-XXX" format
# - Numbered requirements

for req in doc.requirements:
    print(f"{req.id}: {req.description}")
    print(f"Priority: {req.priority}")
    print(f"Found in: {req.section_slug}")
```

## Extension Architecture

The enricher uses a clean extension pattern that allows adding features without modifying the base class:

```python
# Base enricher (original)
class MarkdownDocEnricher:
    """Original enricher - untouched."""
    pass

# Enhanced enricher (extends without modification)
class ContextFixedEnricher(MarkdownDocEnricher):
    """Enhanced with new features."""
    
    def extract_rich_doc(self):
        # Calls parent functionality
        doc = super().extract_rich_doc()
        
        # Adds new extractions
        doc.examples = self._extract_examples()
        doc.definitions = self._extract_definitions()
        
        return doc
```

### Creating Your Own Extensions

```python
from context_fixed_enricher import ContextFixedEnricher

class MyCustomEnricher(ContextFixedEnricher):
    """Add your own extractions."""
    
    def extract_rich_doc(self):
        doc = super().extract_rich_doc()
        
        # Add custom extraction
        doc.custom_data = self._extract_custom()
        
        return doc
    
    def _extract_custom(self):
        # Your custom logic
        pass
```

## API Reference

### Main Class: `ContextFixedEnricher`

```python
class ContextFixedEnricher(MarkdownDocEnricher):
    """Enhanced markdown document enricher."""
    
    def __init__(self, file_path: Union[str, Path]):
        """Initialize with markdown file path."""
    
    def extract_rich_doc(self) -> MarkdownDocExtendedRich:
        """Extract enriched document with all features."""
    
    def get_sections(self) -> List[Section]:
        """Get all sections with hierarchy."""
    
    def get_code_blocks(self) -> List[CodeBlock]:
        """Get all code blocks with metadata."""
    
    def get_examples(self) -> List[CodeExample]:
        """Get classified code examples."""
    
    def get_requirements(self) -> List[Requirement]:
        """Get detected requirements."""
```

### Utility Methods

```python
# Search and filter
def find_section(slug: str) -> Optional[Section]
def find_code_blocks(language: str) -> List[CodeBlock]
def find_examples(type: ExampleType) -> List[CodeExample]

# Analysis
def get_statistics() -> DocumentStats
def get_complexity_score() -> float
def validate_structure() -> List[ValidationIssue]

# Export
def to_json() -> str
def to_dict() -> dict
```

## Examples

### Example 1: Extract Documentation Metrics
```python
from context_fixed_enricher import ContextFixedEnricher

enricher = ContextFixedEnricher("CLAUDE.md")
doc = enricher.extract_rich_doc()

print("Documentation Metrics:")
print(f"├── Sections: {len(doc.sections)}")
print(f"├── Code blocks: {len(doc.code_blocks)}")
print(f"│   ├── Python: {sum(1 for b in doc.code_blocks if b.language == 'python')}")
print(f"│   ├── Bash: {sum(1 for b in doc.code_blocks if b.language == 'bash')}")
print(f"│   └── Other: {sum(1 for b in doc.code_blocks if b.language not in ['python', 'bash'])}")
print(f"├── Examples: {len(doc.examples)}")
print(f"│   ├── Good: {sum(1 for e in doc.examples if e.example_type == 'GOOD')}")
print(f"│   ├── Bad: {sum(1 for e in doc.examples if e.example_type == 'BAD')}")
print(f"│   └── Neutral: {sum(1 for e in doc.examples if e.example_type == 'NEUTRAL')}")
print(f"└── Requirements: {len(doc.requirements)}")
```

### Example 2: Generate Example Report
```python
# Create a report of all good/bad examples
enricher = ContextFixedEnricher("guidelines.md")
doc = enricher.extract_rich_doc()

with open("examples_report.md", "w") as f:
    f.write("# Code Examples Report\n\n")
    
    f.write("## ✅ Good Examples\n\n")
    for ex in doc.examples:
        if ex.example_type == "GOOD":
            f.write(f"### {ex.section_slug}\n")
            f.write(f"```{ex.language}\n{ex.code}\n```\n")
            f.write(f"**Context**: {ex.context_before}\n\n")
    
    f.write("## ❌ Bad Examples\n\n")
    for ex in doc.examples:
        if ex.example_type == "BAD":
            f.write(f"### {ex.section_slug}\n")
            f.write(f"```{ex.language}\n{ex.code}\n```\n")
            f.write(f"**Issue**: {', '.join(ex.patterns_found)}\n\n")
```

### Example 3: Extract for LLM Training
```python
# Prepare training data from examples
import json

enricher = ContextFixedEnricher("best_practices.md")
doc = enricher.extract_rich_doc()

training_data = []

for example in doc.examples:
    if example.example_type in ["GOOD", "BAD"]:
        training_data.append({
            "instruction": example.context_before,
            "input": example.code,
            "output": example.example_type,
            "explanation": example.context_after,
            "patterns": example.patterns_found
        })

with open("training_data.json", "w") as f:
    json.dump(training_data, f, indent=2)
```

### Example 4: Build Knowledge Graph
```python
# Create relationships between sections and code
import networkx as nx

enricher = ContextFixedEnricher("architecture.md")
doc = enricher.extract_rich_doc()

G = nx.DiGraph()

# Add nodes
for section in doc.sections:
    G.add_node(section.slug, type="section", title=section.title)

for block in doc.code_blocks:
    block_id = f"code_{id(block)}"
    G.add_node(block_id, type="code", language=block.language)
    G.add_edge(block.section_slug, block_id, relation="contains")

# Add requirement relationships
for req in doc.requirements:
    G.add_node(req.id, type="requirement", desc=req.description)
    G.add_edge(req.section_slug, req.id, relation="defines")

print(f"Knowledge graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
```

## Performance

### Benchmarks

| Document Size | Parse Time | Memory Usage | Elements Extracted |
|--------------|------------|--------------|-------------------|
| 10 KB | < 0.1s | ~5 MB | ~50 elements |
| 100 KB | < 0.3s | ~15 MB | ~500 elements |
| 1 MB | < 2s | ~50 MB | ~5000 elements |
| 10 MB | < 15s | ~200 MB | ~50000 elements |

### Optimization Tips

```python
# Cache parsed documents
from functools import lru_cache

@lru_cache(maxsize=10)
def get_enriched_doc(path):
    return ContextFixedEnricher(path).extract_rich_doc()

# Process in batches
def process_many_docs(paths):
    for batch in chunks(paths, 10):
        docs = [ContextFixedEnricher(p).extract_rich_doc() 
                for p in batch]
        yield docs
```

## Troubleshooting

### Common Issues

#### 1. Large Documents Slow to Parse
```python
# Solution: Use streaming for very large docs
enricher = ContextFixedEnricher("huge_doc.md")
enricher.streaming_mode = True  # Process in chunks
```

#### 2. Missing Code Examples
```python
# Check pattern detection is working
enricher.debug_mode = True
doc = enricher.extract_rich_doc()
# Will print pattern matching details
```

#### 3. Incorrect Section Hierarchy
```python
# Validate markdown structure
enricher = ContextFixedEnricher("doc.md")
issues = enricher.validate_structure()
for issue in issues:
    print(f"Line {issue.line}: {issue.message}")
```

#### 4. Memory Issues
```python
# Use lightweight extraction
enricher = ContextFixedEnricher("doc.md")
enricher.lightweight = True  # Skip heavy processing
doc = enricher.extract_rich_doc()
```

## Integration with RAG Pipeline

The enricher is the foundation of the RAG pipeline:

```python
from context_fixed_enricher import ContextFixedEnricher
from rag_pipeline import RAGPipeline

# Enricher extracts semantic information
enricher = ContextFixedEnricher("document.md")
doc = enricher.extract_rich_doc()

# RAG pipeline uses enriched content
pipeline = RAGPipeline()

# Convert sections to documents for indexing
documents = []
for section in doc.sections:
    documents.append({
        "content": section.content,
        "metadata": {
            "title": section.title,
            "level": section.level,
            "code_blocks": len(section.code_blocks),
            "has_requirements": len(section.requirements) > 0
        }
    })

pipeline.index_documents(documents)
```

## Best Practices

1. **File Size**: For files > 1MB, consider splitting
2. **Caching**: Cache enriched documents to avoid re-parsing
3. **Validation**: Always validate structure for unknown documents
4. **Error Handling**: Wrap extraction in try/catch for safety
5. **Memory**: Use streaming mode for very large documents

## Future Enhancements

- [ ] Mermaid diagram extraction
- [ ] Math formula detection
- [ ] Cross-reference analysis
- [ ] Multi-language code support
- [ ] Incremental parsing
- [ ] Real-time updates

---

For more information, see:
- [ENRICHED_EXTENSION_PLAN.md](ENRICHED_EXTENSION_PLAN.md) - Development history
- [README.md](README.md) - RAG pipeline documentation
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference