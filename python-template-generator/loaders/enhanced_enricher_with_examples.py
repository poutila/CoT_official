"""Enhanced Markdown Enricher with Example Detection.

This module extends MinimalEnhancedEnricher to add detection of good/bad
code examples and patterns, building on the code block extraction.
"""

import re
from enum import Enum
from pathlib import Path

from minimal_enhanced_enricher import CodeBlock, MinimalEnhancedDoc, MinimalEnhancedEnricher
from pydantic import BaseModel, Field


class ExampleType(str, Enum):
    """Types of examples that can be detected."""

    GOOD = "good"
    BAD = "bad"
    NEUTRAL = "neutral"
    COMPARISON = "comparison"  # Has both good and bad


class CodeExample(BaseModel):
    """Enhanced code block with example classification."""

    content: str = Field(..., description="The code content")
    language: str = Field(default="", description="Programming language")
    section_slug: str = Field(default="", description="Section containing the code")
    line_start: int | None = Field(None, description="Starting line number")
    example_type: ExampleType = Field(default=ExampleType.NEUTRAL, description="Type of example")
    pattern_markers: list[str] = Field(default_factory=list, description="Pattern markers found")
    context_before: str = Field(default="", description="Text before the code block")
    context_after: str = Field(default="", description="Text after the code block")

    @property
    def is_good_example(self) -> bool:
        """Check if this is a good practice example."""
        return self.example_type == ExampleType.GOOD

    @property
    def is_bad_example(self) -> bool:
        """Check if this is an anti-pattern example."""
        return self.example_type == ExampleType.BAD

    @property
    def has_pattern(self) -> bool:
        """Check if this has any pattern markers."""
        return len(self.pattern_markers) > 0


class ExampleEnhancedDoc(MinimalEnhancedDoc):
    """Extends MinimalEnhancedDoc with example detection."""

    code_examples: list[CodeExample] = Field(
        default_factory=list, description="Code blocks with example classification"
    )

    @property
    def good_examples(self) -> list[CodeExample]:
        """Get all good practice examples."""
        return [ex for ex in self.code_examples if ex.is_good_example]

    @property
    def bad_examples(self) -> list[CodeExample]:
        """Get all anti-pattern examples."""
        return [ex for ex in self.code_examples if ex.is_bad_example]

    @property
    def comparison_examples(self) -> list[CodeExample]:
        """Get examples that show comparisons."""
        return [ex for ex in self.code_examples if ex.example_type == ExampleType.COMPARISON]

    @property
    def examples_by_language(self) -> dict[str, list[CodeExample]]:
        """Group examples by programming language."""
        result = {}
        for ex in self.code_examples:
            lang = ex.language or "unspecified"
            if lang not in result:
                result[lang] = []
            result[lang].append(ex)
        return result

    @property
    def pattern_summary(self) -> dict[str, int]:
        """Count of different pattern types found."""
        return {
            "good": len(self.good_examples),
            "bad": len(self.bad_examples),
            "neutral": len(
                [e for e in self.code_examples if e.example_type == ExampleType.NEUTRAL]
            ),
            "comparison": len(self.comparison_examples),
            "total": len(self.code_examples),
        }


class ExampleEnhancedEnricher(MinimalEnhancedEnricher):
    """Enricher that adds example detection to code block extraction.

    This enricher extends MinimalEnhancedEnricher to detect and classify
    code examples as good practices, bad practices, or neutral examples.
    It looks for pattern markers in code and surrounding context.
    """

    # Pattern markers to look for
    GOOD_MARKERS = [
        r"#\s*(?:✅|✓)\s*GOOD",
        r"#\s*(?:✅|✓)\s*Good",
        r"#\s*GOOD:",
        r"#\s*Good:",
        r"#\s*Best practice",
        r"#\s*Recommended",
        r"#\s*DO:",
        r"#\s*Correct:",
        r"✅\s*GOOD",
        r"✅\s*Good",
    ]

    BAD_MARKERS = [
        r"#\s*(?:❌|✗|X)\s*BAD",
        r"#\s*(?:❌|✗|X)\s*Bad",
        r"#\s*BAD:",
        r"#\s*Bad:",
        r"#\s*Anti-pattern",
        r"#\s*Avoid",
        r"#\s*DON\'T:",
        r"#\s*DONT:",
        r"#\s*Wrong:",
        r"#\s*Incorrect:",
        r"❌\s*BAD",
        r"❌\s*Bad",
    ]

    COMPARISON_MARKERS = [
        r"#\s*Before[:\s]",
        r"#\s*After[:\s]",
        r"#\s*Old[:\s]",
        r"#\s*New[:\s]",
        r"#\s*Instead of[:\s]",
        r"#\s*Better[:\s]",
    ]

    def __init__(self, path: Path):
        """Initialize enricher with document path."""
        super().__init__(path)
        self._context_cache = {}  # Cache for context extraction

    def extract_rich_doc(self) -> ExampleEnhancedDoc:
        """Extract document with code examples and pattern detection.

        Returns:
            ExampleEnhancedDoc with code blocks classified as examples
        """
        # Get base document with code blocks
        base_doc = super().extract_rich_doc()

        # Enhance code blocks with example detection
        code_examples = self._enhance_code_blocks_with_examples(base_doc.code_blocks)

        # Return enhanced document
        return ExampleEnhancedDoc(
            **base_doc.model_dump(exclude={"code_blocks"}),
            code_blocks=base_doc.code_blocks,  # Keep original for compatibility
            code_examples=code_examples,  # Add enhanced examples
        )

    def _enhance_code_blocks_with_examples(self, code_blocks: list[CodeBlock]) -> list[CodeExample]:
        """Enhance code blocks with example detection and classification.

        Args:
            code_blocks: List of basic code blocks from parent

        Returns:
            List of CodeExample objects with pattern detection
        """
        examples = []

        for block in code_blocks:
            # Detect patterns in the code content
            example_type, markers = self._detect_example_patterns(block.content)

            # Get surrounding context (if available)
            context_before, context_after = self._get_block_context(block)

            # Check context for patterns if not found in code
            if example_type == ExampleType.NEUTRAL and context_before:
                context_type, context_markers = self._detect_example_patterns(context_before)
                if context_type != ExampleType.NEUTRAL:
                    example_type = context_type
                    markers.extend(context_markers)

            # Create enhanced example
            example = CodeExample(
                content=block.content,
                language=block.language,
                section_slug=block.section_slug,
                line_start=block.line_start,
                example_type=example_type,
                pattern_markers=markers,
                context_before=context_before[:200] if context_before else "",  # Limit context size
                context_after=context_after[:200] if context_after else "",
            )

            examples.append(example)

        return examples

    def _detect_example_patterns(self, text: str) -> tuple[ExampleType, list[str]]:
        """Detect example patterns in text.

        Args:
            text: Text to analyze for patterns

        Returns:
            Tuple of (example_type, list_of_markers_found)
        """
        markers_found = []
        has_good = False
        has_bad = False

        # Check for good patterns
        for pattern in self.GOOD_MARKERS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                has_good = True
                markers_found.append(pattern)

        # Check for bad patterns
        for pattern in self.BAD_MARKERS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                has_bad = True
                markers_found.append(pattern)

        # Check for comparison patterns
        for pattern in self.COMPARISON_MARKERS:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                markers_found.append(pattern)

        # Determine type
        if has_good and has_bad:
            return ExampleType.COMPARISON, markers_found
        if has_good:
            return ExampleType.GOOD, markers_found
        if has_bad:
            return ExampleType.BAD, markers_found
        return ExampleType.NEUTRAL, markers_found

    def _get_block_context(self, block: CodeBlock) -> tuple[str, str]:
        """Get text context before and after a code block.

        Args:
            block: Code block to get context for

        Returns:
            Tuple of (text_before, text_after)
        """
        # This is a simplified version - could be enhanced to track actual positions
        # For now, return empty context
        # In a full implementation, we'd track node positions and extract surrounding text
        return "", ""

    def get_examples_by_type(self, example_type: ExampleType) -> list[CodeExample]:
        """Get all examples of a specific type.

        Args:
            example_type: Type of examples to retrieve

        Returns:
            List of examples matching the type
        """
        doc = self.extract_rich_doc()
        return [ex for ex in doc.code_examples if ex.example_type == example_type]

    def get_pattern_statistics(self) -> dict[str, any]:
        """Get statistics about patterns found in the document.

        Returns:
            Dictionary with pattern statistics
        """
        doc = self.extract_rich_doc()

        stats = {
            "total_code_blocks": len(doc.code_blocks),
            "total_examples": len(doc.code_examples),
            "pattern_summary": doc.pattern_summary,
            "languages_with_examples": {},
            "sections_with_patterns": set(),
        }

        # Count examples per language
        for lang, examples in doc.examples_by_language.items():
            stats["languages_with_examples"][lang] = {
                "total": len(examples),
                "good": len([e for e in examples if e.is_good_example]),
                "bad": len([e for e in examples if e.is_bad_example]),
            }

        # Track sections with patterns
        for ex in doc.code_examples:
            if ex.has_pattern and ex.section_slug:
                stats["sections_with_patterns"].add(ex.section_slug)

        stats["sections_with_patterns"] = list(stats["sections_with_patterns"])

        return stats


def test_example_detection():
    """Test the example detection enricher."""
    import json

    print("=" * 60)
    print("Testing Enhanced Enricher with Example Detection")
    print("=" * 60)

    # Test with CLAUDE.md
    claude_path = Path("CLAUDE.md")
    if not claude_path.exists():
        print(f"Error: {claude_path} not found")
        return False

    try:
        # Create enricher
        print(f"\nProcessing: {claude_path}")
        enricher = ExampleEnhancedEnricher(claude_path)

        # Extract enhanced document
        print("Extracting document with example detection...")
        doc = enricher.extract_rich_doc()

        # Show results
        print("\nParent Features Preserved:")
        print(f"  - Sections: {len(doc.sections)}")
        print(f"  - Total code blocks: {doc.total_code_blocks}")

        print("\nExample Detection Results:")
        print(f"  - Total examples analyzed: {len(doc.code_examples)}")
        print(f"  - Pattern summary: {doc.pattern_summary}")

        # Show good examples
        if doc.good_examples:
            print(f"\nGood Practice Examples Found: {len(doc.good_examples)}")
            for i, ex in enumerate(doc.good_examples[:3], 1):
                print(f"  Example {i}:")
                print(f"    Language: {ex.language}")
                print(f"    Section: {ex.section_slug}")
                print(f"    Markers: {ex.pattern_markers[:2] if ex.pattern_markers else 'None'}")
                print(f"    Preview: {ex.content[:60]}...")

        # Show bad examples
        if doc.bad_examples:
            print(f"\nAnti-Pattern Examples Found: {len(doc.bad_examples)}")
            for i, ex in enumerate(doc.bad_examples[:3], 1):
                print(f"  Example {i}:")
                print(f"    Language: {ex.language}")
                print(f"    Section: {ex.section_slug}")
                print(f"    Markers: {ex.pattern_markers[:2] if ex.pattern_markers else 'None'}")
                print(f"    Preview: {ex.content[:60]}...")

        # Get statistics
        stats = enricher.get_pattern_statistics()
        print("\nPattern Statistics:")
        print(f"  - Sections with patterns: {len(stats['sections_with_patterns'])}")
        print("  - Languages with examples:")
        for lang, counts in stats["languages_with_examples"].items():
            print(
                f"    {lang}: {counts['total']} total ({counts['good']} good, {counts['bad']} bad)"
            )

        # Save results
        output_path = Path("example_enhanced_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            output_data = {
                "document": claude_path.name,
                "pattern_summary": doc.pattern_summary,
                "good_examples": [
                    {
                        "language": ex.language,
                        "section": ex.section_slug,
                        "markers": ex.pattern_markers[:2] if ex.pattern_markers else [],
                        "preview": ex.content[:100],
                    }
                    for ex in doc.good_examples[:5]
                ],
                "bad_examples": [
                    {
                        "language": ex.language,
                        "section": ex.section_slug,
                        "markers": ex.pattern_markers[:2] if ex.pattern_markers else [],
                        "preview": ex.content[:100],
                    }
                    for ex in doc.bad_examples[:5]
                ],
                "statistics": stats,
            }
            json.dump(output_data, f, indent=2, ensure_ascii=True)  # Use ASCII for safety

        print(f"\nResults saved to: {output_path}")
        print("\nSuccess! Example detection working on top of code extraction.")
        return True

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the enhanced enricher
    success = test_example_detection()

    if success:
        print("\nExample Detection Complete!")
        print("Next steps:")
        print("  1. Add context extraction (surrounding paragraphs)")
        print("  2. Add context window optimization")
        print("  3. Integrate with semantic engine")
    else:
        print("\nExample detection needs debugging.")
