import re
from pathlib import Path

from markdown_base_validator import MarkdownDocumentValidator
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from markdown_pydantic_model import (
    ChecklistItem,
    MarkdownDoc,
    MarkdownDocExtendedRich,
    MarkdownSection,
    MarkdownSectionRich,
    MarkdownTable,
    MarkdownTableRow,
    Requirement,
)
from pydantic import ValidationError


class MarkdownDocEnricher(MarkdownDocumentValidator):
    def __init__(self, path: Path):
        super().__init__(path)
        self.base_md_doc: MarkdownDoc = super().parse_md()

    @staticmethod
    def walk_tree(node, level=0):
        # if node.type == "text":
        print("==" * level + f"{level}- type: {node.type}: content: ( {node.content!r} )")
        for child in node.children or []:
            MarkdownDocEnricher.walk_tree(child, level + 1)

    @staticmethod
    def extract_table(node: SyntaxTreeNode) -> MarkdownTable:
        header = []
        rows = []

        for child in node.children or []:
            if child.type == "thead":
                for tr in child.children or []:
                    header = [
                        "".join(grandchild.content for grandchild in (th.children or []))
                        for th in tr.children or []
                    ]
            elif child.type == "tbody":
                for tr in child.children or []:
                    row = []
                    for td in tr.children or []:
                        cell = "".join(grandchild.content for grandchild in (td.children or []))
                        row.append(cell)
                    rows.append(MarkdownTableRow(cells=row))

        return MarkdownTable(header=header, rows=rows)

    def extract_rich_doc(self) -> MarkdownDocExtendedRich:
        """Extracts rich MarkdownDoc with additional metadata and structured sections."""
        base_sections: list[MarkdownSection] = self.base_md_doc.sections
        sections_rich: list[MarkdownSectionRich] = []
        current: MarkdownSectionRich | None = None
        md = MarkdownIt().enable("table")
        requirement_pattern = re.compile(r".*(MUST NOT|MUST|SHOULD|MAY).*", re.IGNORECASE)
        check_list_pattern = re.compile(r".*(\[-\]|\[( |x)\])", re.IGNORECASE)

        print(f"Total sections: {len(base_sections)}")
        for section in base_sections:
            content = section.content.strip()
            tree = SyntaxTreeNode(md.parse(content))
            current = MarkdownSectionRich(
                level=section.level,
                title=section.title,
                slug=section.slug,
                content=section.content,
                requirements=[],
                checklist_items=[],
                block_types=[],
                links={},
            )

            for node in tree.walk(include_self=False):
                # Extract tables
                if node.type == "table":
                    table = self.extract_table(node)
                    if table.header or table.rows:
                        current.tables.append(table)
                        continue

                # Process links
                if node.type == "link":
                    link = super().process_node(node)
                    if link not in [None, ("", None)]:
                        validated = super().validate_links([link])
                        if len(current.links) == 0:
                            current.links = validated
                        else:
                            for key, value in validated.items():
                                if len(value) > 0:
                                    current.links.setdefault(key, []).append(value[0])
                                    continue

                if node.type in {"paragraph", "bullet_list", "fence", "code_block"}:
                    block = node.content or "".join(c.content for c in (node.children or []))
                    current.block_types.append(node.type)
                    current.content += block + "\n"

                    # Extract requirements and checklist items
                    for line in block.splitlines():
                        matches = list(requirement_pattern.finditer(line))
                        for match in matches:
                            # print(f"Requirement found: {match}")
                            current.requirements.append(
                                Requirement(
                                    rule_text=line.strip(),
                                    type=match.group(1).upper(),
                                    source_block=block.strip(),
                                )
                            )

                        checklist_match = re.match(check_list_pattern, line)
                        if checklist_match:
                            checked = False
                            checked_value = checklist_match.group(0).lower()
                            if any(x in checked_value for x in ["x", "X"]):
                                checked = True
                            current.checklist_items.append(
                                ChecklistItem(text=line.strip(), checked=checked)
                            )

            sections_rich.append(current)

        for i, section in enumerate(sections_rich):
            if i > 0:
                section.previous_slug = sections_rich[i - 1].slug
            if i < len(sections_rich) - 1:
                section.next_slug = sections_rich[i + 1].slug
        try:
            return MarkdownDocExtendedRich(
                **self.base_md_doc.model_dump(exclude={"sections"}),
                sections=sections_rich,
                meta={
                    "line_count": self.content.count("\n"),
                    "word_count": len(self.content.split()),
                    "section_count": len(sections_rich),
                    "link_count": sum(len(s.links) for s in sections_rich),
                },
            )
        except ValidationError as exc:
            print(repr(exc.errors()[0]["type"]))
            # raise exc


if __name__ == "__main__":
    print("MarkdownDocEnricher module is not intended to be run directly.")
