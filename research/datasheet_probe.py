"""Reproducible research probe; counts extraction structure without accepting electrical limits."""

import argparse
import hashlib
import json
from pathlib import Path


def main():
    import pymupdf

    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stats = []
    with pymupdf.open(args.document) as document:
        for page in document:
            text = page.get_text("text", sort=True)
            if "Electrical Characteristics" in text and len(text) > 1000:
                tables = page.find_tables().tables
                stats.append(
                    {
                        "page": page.number + 1,
                        "text_characters": len(text),
                        "word_boxes": len(page.get_text("words")),
                        "detected_tables": len(tables),
                        "table_shapes": [[t.row_count, t.col_count] for t in tables],
                        "empty_cells": sum(
                            cell in ("", None)
                            for t in tables
                            for row in t.extract()
                            for cell in row
                        ),
                    }
                )
    result = {
        "document_sha256": hashlib.sha256(args.document.read_bytes()).hexdigest(),
        "pymupdf_version": pymupdf.VersionBind,
        "pages": stats,
        "conclusion": "Structural extraction only; no electrical constraint accepted automatically",
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
