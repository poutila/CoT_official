from pathlib import Path

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from .pydantic_models import MarkdownDoc, MarkdownSection
from utils.sluggify import slugify


class MarkdownDocumentValidator:
    def __init__(self, path: Path):
        self.md = MarkdownIt()
        self.path = path
        self.content = path.read_text(encoding="utf-8")
        self.tree = SyntaxTreeNode(self.md.parse(self.content))
        self.walk = self.tree.walk(include_self=False)
        self.doc_cache: dict[Path, MarkdownDoc] = {}

    def validate_links(self, links: list[tuple[str, str | None]]) -> dict[str, list[str]]:
        """
        Validate that all links in the MarkdownDoc point to existing files and anchors.
        Returns a dict with keys: 'valid_file', 'invalid_file', 'invalid_anchor'
        """
        results: dict[str, list[str | Path]] = {"valid_file": [], "invalid_file": [], "invalid_anchor": []}
        current_path = self.path.resolve().parent
        # print(f"Validating links in: {current_path} {self.path}")
        links_cleaned = [x for x in links if x not in [None]]
        print(f"{links_cleaned}")
        for file_part, anchor in links_cleaned:
            # print(f"\nValidating link: {file_part}, anchor: {anchor}")
            target_path = current_path / file_part
            print(f"Target path: {target_path}")
            if target_path.is_file() or target_path.is_dir():
                results["valid_file"].append(Path(file_part))
            else:
                results["invalid_file"].append(Path(file_part))

            if anchor:
                if target_path not in self.doc_cache:
                    self.doc_cache[target_path] = MarkdownDocumentValidator(
                        target_path
                    ).parse_md()
                if not self.validate_anchor(anchor, self.doc_cache[target_path]):
                    results["invalid_anchor"].append(f"{file_part}#{anchor}")
                    continue

        # print(f"results: {results}")
        return results

    def validate_anchor(self, anchor: str, md: MarkdownDoc) -> bool:
        return anchor in {s.slug for s in md.sections}

    def process_node(self, node: SyntaxTreeNode) -> tuple[str, str | None] | None:
        """
        Process a single node to extract section information.
        """
        if node.type == "link" and node.children:
            href = node.attrs.get("href")  # type: ignore[attr-defined]
            if href and isinstance(href, str) and not href.startswith(("http:", "https:")):
                file, anchor = href.split("#", 1) if "#" in href else (href, None)
                return (file.strip(), anchor.strip() if anchor else None)
        return None

    def parse_md(self) -> MarkdownDoc:
        """Extract sections from markdown file using AST."""

        sections = []
        links = []
        current_section: MarkdownSection | None = None

        for node in self.walk:
            if node.type == "link":
                links.append(self.process_node(node))

            if node.type == "heading" and node.children:
                # Save previous section
                if current_section:
                    sections.append(current_section)

                heading_text = "".join(child.content for child in node.children).strip()
                level = int(node.markup.count("#"))
                current_section = MarkdownSection(
                    level=level,
                    title=heading_text,
                    content="",
                    slug=slugify(heading_text),
                )
            elif current_section and node.type == "paragraph":
                para = "".join(child.content for child in node.children or [])
                current_section.content += para + "\n"

        if current_section:
            sections.append(current_section)
        validated_links = self.validate_links([link for link in links if link is not None])
        headings_structure_valid = True
        headings_levels = [x.level for x in sections]
        for index in range(1, len(headings_levels)):
            prev = headings_levels[index - 1]
            curr = headings_levels[index]
            if curr > prev + 1:
                headings_structure_valid = False
                break
        return MarkdownDoc(
            path=self.path,
            content=self.content,
            sections=sections,
            links=validated_links,  # type: ignore[arg-type]
            heading_structure_valid=headings_structure_valid,
        )


if __name__ == "__main__":
    base = Path(__file__).parent.parent.parent.parent

    validator = MarkdownDocumentValidator(base / "CLAUDE.md")
    # print(validator.get_links())

    doc = validator.parse_md()
    for item in doc.sections:
        print(f"Section title: {item.title} (Level: {item.level})")
        print(f"Slug: {item.slug}")
        print(f"Content: {item.content[:200]}...\n")

    print(f"All links exist: {doc.all_links_exist}")
    # print(f"Number of non-existing links: {doc.number_of_non_existing_links}")
    print(f"Document links: {doc.links}")
    print(f"Heading structure valid: {doc.heading_structure_valid}")
    # print(MarkdownDocumentValidator(base / "CLAUDE.md").parse_md().sections)
    # Path("output.json").write_text(doc.model_dump_json(indent=2), encoding="utf-8")
