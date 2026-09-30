from dataclasses import dataclass
from pathlib import Path

SUPPORTED = {".txt", ".md"}


@dataclass
class Document:
    name: str   # path relative to docs/, shown in citations
    text: str


def load_documents(folder: Path) -> list[Document]:
    """Read every .txt/.md file under folder, sorted by path."""
    docs = []
    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            # utf-8-sig so files saved with a BOM on Windows still read cleanly
            text = path.read_text(encoding="utf-8-sig").strip()
            if text:
                docs.append(Document(path.relative_to(folder).as_posix(), text))
    return docs
