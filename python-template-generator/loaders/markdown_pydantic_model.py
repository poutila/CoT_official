from pydantic import BaseModel, field_validator, Field
from typing import Dict, List, Union, Optional, Literal
from pathlib import Path


class Requirement(BaseModel):
    rule_text: str
    type: Literal["MUST", "SHOULD", "MUST NOT", "MAY"]
    source_block: str


class ChecklistItem(BaseModel):
    text: str
    checked: bool

class MarkdownTableRow(BaseModel):
    cells: List[str]

class MarkdownTable(BaseModel):
    header: List[str]
    rows: List[MarkdownTableRow]


class MarkdownSection(BaseModel):
    level: int = Field(..., ge=1, le=6)
    title: str
    content: str
    slug: str


class MarkdownSectionRich(MarkdownSection):
    requirements: List[Requirement] = []
    checklist_items: List[ChecklistItem] = []
    block_types: List[str] = []
    links: Dict[str, List[Path]] = Field(default_factory=dict)
    tables: List[MarkdownTable] = Field(default_factory=list)
    previous_slug: Optional[str] = None
    next_slug: Optional[str] = None


class MarkdownDoc(BaseModel):
    path: Path
    content: str
    links: dict[str, List[Union[Path, str]]] = Field(default_factory=dict)
    sections: List[MarkdownSection]
    heading_structure_valid: bool = Field(default=False, description="Indicates if the heading structure is valid.")

    @property
    def all_links_exist(self) -> bool:
        return not bool(len(self.links.get("invalid_file", [])))

    @property
    def invalid_file_links(self) -> List[Path]:
        return self.links.get("invalid_file", [])

    @property
    def valid_file_links(self) -> List[Path]:
        return self.links.get("valid_file", [])
    
    @property
    def invalid_anchor_links(self) -> List[str]:
        return self.links.get("invalid_anchor", [])
    
class MarkdownDocExtendedRich(MarkdownDoc):
    sections: List[MarkdownSectionRich]
    meta: dict[str, Union[int, str]] = {}  # e.g. {"word_count": 6022, "section_count": 49}
