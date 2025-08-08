from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    rule_text: str
    type: Literal["MUST", "SHOULD", "MUST NOT", "MAY"]
    source_block: str


class ChecklistItem(BaseModel):
    text: str
    checked: bool


class MarkdownTableRow(BaseModel):
    cells: list[str]


class MarkdownTable(BaseModel):
    header: list[str]
    rows: list[MarkdownTableRow]


class MarkdownSection(BaseModel):
    level: int = Field(..., ge=1, le=6)
    title: str
    content: str
    slug: str


class MarkdownSectionRich(MarkdownSection):
    requirements: list[Requirement] = []
    checklist_items: list[ChecklistItem] = []
    block_types: list[str] = []
    links: dict[str, list[Path]] = Field(default_factory=dict)
    tables: list[MarkdownTable] = Field(default_factory=list)
    previous_slug: str | None = None
    next_slug: str | None = None


class MarkdownDoc(BaseModel):
    path: Path
    content: str
    links: dict[str, list[Path | str]] = Field(default_factory=dict)
    sections: list[MarkdownSection]
    heading_structure_valid: bool = Field(
        default=False, description="Indicates if the heading structure is valid."
    )

    @property
    def all_links_exist(self) -> bool:
        return not bool(len(self.links.get("invalid_file", [])))

    @property
    def invalid_file_links(self) -> list[Path]:
        links = self.links.get("invalid_file", [])
        return [cast(Path, link) for link in links if isinstance(link, Path)]

    @property
    def valid_file_links(self) -> list[Path]:
        links = self.links.get("valid_file", [])
        return [cast(Path, link) for link in links if isinstance(link, Path)]

    @property
    def invalid_anchor_links(self) -> list[str]:
        links = self.links.get("invalid_anchor", [])
        return [cast(str, link) for link in links if isinstance(link, str)]


class MarkdownDocExtendedRich(MarkdownDoc):
    sections: list[MarkdownSectionRich]  # type: ignore[assignment]
    meta: dict[str, int | str] = {}  # e.g. {"word_count": 6022, "section_count": 49}
