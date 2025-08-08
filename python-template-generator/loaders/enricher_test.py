"""MarkdownDocEnricher Module testing file"""

import sys
from pathlib import Path
from typing import List, Optional

from markdown_validator_enricher import MarkdownDocEnricher


def markdown_doc_enricher_test(
    document_path: str,
) -> None:
    """Get MarkdownDocEnricher instance and print its fields.

    Args:
        document_path: Path to reference markdown document
    """
    md_enricher_doc = MarkdownDocEnricher(Path(document_path)).extract_rich_doc()
    print(f"📄 Document Path: {document_path}")
    json_path = Path("output.json")
    print(f"📄 JSON Output Path: {json_path}")
    json_path.write_text(md_enricher_doc.model_dump_json(indent=2), encoding="utf-8")



def main():
    print(sys.argv)
    document_path = sys.argv[1]
    if not document_path:
        print("Please provide a path to the markdown document.")
        return
    markdown_doc_enricher_test(document_path)

if __name__ == "__main__":
    main()
