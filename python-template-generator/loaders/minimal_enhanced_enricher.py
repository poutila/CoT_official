"""Minimal MVP for Enhanced Markdown Enricher.

This module extends MarkdownDocEnricher to add code block extraction
without modifying the parent class. Proof of concept for extensibility.
"""

from pathlib import Path

from markdown_pydantic_model import MarkdownDocExtendedRich
from markdown_validator_enricher import MarkdownDocEnricher
from pydantic import BaseModel, Field


class CodeBlock(BaseModel):
    """Simple code block model."""

    content: str = Field(..., description="The code content")
    language: str = Field(default="", description="Programming language")
    section_slug: str = Field(default="", description="Section containing the code")
    line_start: int | None = Field(None, description="Starting line number")


class MinimalEnhancedDoc(MarkdownDocExtendedRich):
    """Extends base doc with just code blocks."""

    code_blocks: list[CodeBlock] = Field(default_factory=list, description="Extracted code blocks")

    @property
    def total_code_blocks(self) -> int:
        """Total number of code blocks in document."""
        return len(self.code_blocks)

    @property
    def code_languages(self) -> set:
        """Unique programming languages found."""
        return {cb.language for cb in self.code_blocks if cb.language}

    @property
    def has_code(self) -> bool:
        """Check if document contains code blocks."""
        return len(self.code_blocks) > 0


class MinimalEnhancedEnricher(MarkdownDocEnricher):
    """Minimal proof of concept - adds ONLY code block extraction.

    This enricher extends the base MarkdownDocEnricher without modifying it,
    demonstrating the Open/Closed Principle. It adds extraction of code blocks
    while preserving all parent functionality.
    """

    def __init__(self, path: Path):
        """Initialize enricher with document path."""
        super().__init__(path)
        self._current_section_slug = ""
        self._line_counter = 0

    def extract_rich_doc(self) -> MinimalEnhancedDoc:
        """Extract document with code block enhancement.

        Returns:
            MinimalEnhancedDoc with all parent features plus code blocks
        """
        # Get everything from parent enricher
        base_doc = super().extract_rich_doc()

        # Add ONE enhancement: extract code blocks
        code_blocks = self._extract_code_blocks()

        # Return enhanced document combining parent data with new features
        return MinimalEnhancedDoc(**base_doc.model_dump(), code_blocks=code_blocks)

    def _extract_code_blocks(self) -> list[CodeBlock]:
        """Extract only code blocks - simple and focused.

        Returns:
            List of CodeBlock objects found in document
        """
        blocks = []
        current_line = 0
        current_section = ""

        # Walk the syntax tree to find code blocks
        for node in self.tree.walk(include_self=False):
            # Track current section for context
            if node.type == "heading" and node.children:
                heading_text = "".join(
                    child.content for child in node.children if hasattr(child, "content")
                ).strip()
                # Simple slug generation (could reuse parent's slugify)
                current_section = heading_text.lower().replace(" ", "-")

            # Extract fence code blocks (```language ... ```)
            if node.type == "fence":
                # Get language from info string (e.g., ```python)
                language = ""
                if hasattr(node, "info") and node.info:
                    language = node.info.strip().split()[0] if node.info.strip() else ""

                # Get code content
                content = ""
                if hasattr(node, "content") and node.content:
                    content = node.content

                # Create code block
                blocks.append(
                    CodeBlock(
                        content=content,
                        language=language,
                        section_slug=current_section,
                        line_start=current_line,
                    )
                )

            # Track line numbers (approximate)
            if hasattr(node, "content") and node.content:
                current_line += node.content.count("\n") + 1

        return blocks

    def get_code_by_language(self, language: str) -> list[CodeBlock]:
        """Get all code blocks of a specific language.

        Args:
            language: Programming language to filter by

        Returns:
            List of code blocks matching the language
        """
        doc = self.extract_rich_doc()
        return [cb for cb in doc.code_blocks if cb.language == language]

    def get_code_in_section(self, section_slug: str) -> list[CodeBlock]:
        """Get all code blocks in a specific section.

        Args:
            section_slug: Section identifier to filter by

        Returns:
            List of code blocks in the section
        """
        doc = self.extract_rich_doc()
        return [cb for cb in doc.code_blocks if cb.section_slug == section_slug]


def test_minimal_mvp():
    """Quick test of the minimal MVP with CLAUDE.md."""
    import json

    print("=" * 60)
    print("Testing Minimal Enhanced Enricher MVP")
    print("=" * 60)

    # Test with CLAUDE.md
    claude_path = Path("CLAUDE.md")
    if not claude_path.exists():
        print(f"❌ {claude_path} not found")
        return False

    try:
        # Create enricher
        print(f"\n📄 Processing: {claude_path}")
        enricher = MinimalEnhancedEnricher(claude_path)

        # Extract enhanced document
        print("🔄 Extracting document with enhancements...")
        doc = enricher.extract_rich_doc()

        # Verify parent features still work
        print("\n✅ Parent Features Preserved:")
        print(f"  - Sections: {len(doc.sections)}")
        print(f"  - Links: {len(doc.links)}")
        print(f"  - Heading structure valid: {doc.heading_structure_valid}")

        # Check new enhancement
        print("\n🆕 New Enhancement - Code Blocks:")
        print(f"  - Total code blocks: {doc.total_code_blocks}")
        print(f"  - Languages found: {doc.code_languages}")
        print(f"  - Has code: {doc.has_code}")

        # Show sample code blocks
        if doc.code_blocks:
            print("\n📝 Sample Code Blocks:")
            for i, cb in enumerate(doc.code_blocks[:3], 1):
                print(f"\n  Block {i}:")
                print(f"    Language: {cb.language or 'none'}")
                print(f"    Section: {cb.section_slug or 'root'}")
                print(f"    Line: {cb.line_start}")
                print(
                    f"    Preview: {cb.content[:50]}..."
                    if len(cb.content) > 50
                    else f"    Content: {cb.content}"
                )

        # Language statistics
        if doc.code_languages:
            print("\n📊 Language Distribution:")
            lang_counts = {}
            for cb in doc.code_blocks:
                lang = cb.language or "unspecified"
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"    {lang}: {count} blocks")

        # Save enhanced output
        output_path = Path("minimal_enhanced_output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            output_data = {
                "document": claude_path.name,
                "sections_count": len(doc.sections),
                "code_blocks_count": doc.total_code_blocks,
                "languages": list(doc.code_languages),
                "code_blocks": [
                    {
                        "language": cb.language,
                        "section": cb.section_slug,
                        "line_start": cb.line_start,
                        "content_preview": cb.content[:100] + "..."
                        if len(cb.content) > 100
                        else cb.content,
                    }
                    for cb in doc.code_blocks
                ],
            }
            json.dump(output_data, f, indent=2)
        print(f"\n💾 Enhanced output saved to: {output_path}")

        print("\n✅ MVP Success! Extension works without breaking parent.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run test when module is executed directly
    success = test_minimal_mvp()

    if success:
        print("\n🎉 Minimal MVP Complete!")
        print("Next steps:")
        print("  1. Add example detection (good/bad patterns)")
        print("  2. Add context window optimization")
        print("  3. Create comprehensive tests")
    else:
        print("\n⚠️ MVP needs debugging before proceeding.")
