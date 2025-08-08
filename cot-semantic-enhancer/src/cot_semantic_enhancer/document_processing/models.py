"""Pydantic models for document processing."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Literal
from pathlib import Path
from datetime import datetime


class Requirement(BaseModel):
    """A requirement extracted from document."""
    rule_text: str = Field(..., description="The full text of the requirement")
    type: Literal["MUST", "SHOULD", "MUST NOT", "MAY", "SHALL", "SHALL NOT"] = Field(
        ..., description="RFC 2119 requirement level"
    )
    source_section: str = Field(..., description="Section where requirement was found")
    line_number: Optional[int] = Field(None, description="Line number in source")
    context: Optional[str] = Field(None, description="Surrounding context")


class ChecklistItem(BaseModel):
    """A checklist item from markdown."""
    text: str = Field(..., description="Checklist item text")
    checked: bool = Field(..., description="Whether item is checked")
    section: str = Field(..., description="Section containing the item")
    indent_level: int = Field(0, description="Indentation level")


class MarkdownTableRow(BaseModel):
    """A row in a markdown table."""
    cells: List[str] = Field(..., description="Cell values")


class MarkdownTable(BaseModel):
    """A markdown table structure."""
    header: List[str] = Field(..., description="Header row")
    rows: List[MarkdownTableRow] = Field(..., description="Data rows")
    section: str = Field(..., description="Section containing the table")
    caption: Optional[str] = Field(None, description="Table caption if present")


class DocumentSection(BaseModel):
    """A section within a document."""
    level: int = Field(..., ge=1, le=6, description="Heading level (1-6)")
    title: str = Field(..., description="Section title")
    slug: str = Field(..., description="URL-safe section identifier")
    content: str = Field(..., description="Section content")
    requirements: List[Requirement] = Field(default_factory=list)
    checklists: List[ChecklistItem] = Field(default_factory=list)
    tables: List[MarkdownTable] = Field(default_factory=list)
    subsections: List["DocumentSection"] = Field(default_factory=list)
    parent_slug: Optional[str] = Field(None, description="Parent section slug")


class SemanticChunk(BaseModel):
    """A semantic chunk of a document."""
    content: str = Field(..., description="Chunk content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    type: Literal["text", "requirement", "checklist", "table", "code"] = Field(
        "text", description="Type of chunk"
    )
    section_path: List[str] = Field(
        default_factory=list, description="Path of section titles"
    )
    start_line: Optional[int] = Field(None, description="Starting line number")
    end_line: Optional[int] = Field(None, description="Ending line number")
    embedding: Optional[List[float]] = Field(None, description="Pre-computed embedding")


class DocumentLink(BaseModel):
    """A link within a document."""
    text: str = Field(..., description="Link text")
    target: str = Field(..., description="Link target (URL or path)")
    type: Literal["internal", "external", "anchor"] = Field(..., description="Link type")
    is_valid: bool = Field(True, description="Whether link is valid")
    section: str = Field(..., description="Section containing the link")


class DocumentMetadata(BaseModel):
    """Metadata about a document."""
    path: Path = Field(..., description="Document file path")
    title: Optional[str] = Field(None, description="Document title")
    word_count: int = Field(..., description="Total word count")
    line_count: int = Field(..., description="Total line count")
    section_count: int = Field(..., description="Number of sections")
    requirement_count: int = Field(..., description="Number of requirements")
    checklist_count: int = Field(..., description="Number of checklist items")
    table_count: int = Field(..., description="Number of tables")
    link_count: int = Field(..., description="Number of links")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    modified_at: Optional[datetime] = Field(None, description="Last modification time")
    language: str = Field("en", description="Document language")


class SemanticDocument(BaseModel):
    """A semantically enriched document."""
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    content: str = Field(..., description="Full document content")
    sections: List[DocumentSection] = Field(..., description="Document sections")
    requirements: List[Requirement] = Field(
        default_factory=list, description="All requirements"
    )
    checklists: List[ChecklistItem] = Field(
        default_factory=list, description="All checklist items"
    )
    tables: List[MarkdownTable] = Field(
        default_factory=list, description="All tables"
    )
    links: List[DocumentLink] = Field(
        default_factory=list, description="All links"
    )
    chunks: List[SemanticChunk] = Field(
        default_factory=list, description="Semantic chunks"
    )
    
    @property
    def all_links_valid(self) -> bool:
        """Check if all links are valid."""
        return all(link.is_valid for link in self.links)
    
    @property
    def has_requirements(self) -> bool:
        """Check if document has requirements."""
        return len(self.requirements) > 0
    
    @property
    def completion_rate(self) -> float:
        """Calculate checklist completion rate."""
        if not self.checklists:
            return 1.0
        checked = sum(1 for item in self.checklists if item.checked)
        return checked / len(self.checklists)
    
    def get_section_by_slug(self, slug: str) -> Optional[DocumentSection]:
        """Get section by slug."""
        def search_sections(sections: List[DocumentSection]) -> Optional[DocumentSection]:
            for section in sections:
                if section.slug == slug:
                    return section
                if section.subsections:
                    result = search_sections(section.subsections)
                    if result:
                        return result
            return None
        
        return search_sections(self.sections)
    
    def get_requirements_by_type(
        self, req_type: Literal["MUST", "SHOULD", "MUST NOT", "MAY", "SHALL", "SHALL NOT"]
    ) -> List[Requirement]:
        """Get requirements by type."""
        return [req for req in self.requirements if req.type == req_type]


# Enable forward references
DocumentSection.model_rebuild()