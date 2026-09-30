import re
from dataclasses import dataclass

from .config import CHUNK_WORDS, OVERLAP_WORDS
from .loader import Document

_HEADING = re.compile(r"^#{1,6}\s+(.*)$")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    source: str    # file name
    section: str   # nearest markdown heading, empty if none
    text: str


def _words(text: str) -> int:
    return len(text.split())


def _split_long(paragraph: str) -> list[str]:
    """Split an over-long paragraph on sentence boundaries."""
    if _words(paragraph) <= CHUNK_WORDS:
        return [paragraph]
    pieces, buf = [], []
    for sentence in _SENTENCE_END.split(paragraph):
        buf.append(sentence)
        if sum(_words(s) for s in buf) >= CHUNK_WORDS:
            pieces.append(" ".join(buf))
            buf = []
    if buf:
        pieces.append(" ".join(buf))
    return pieces


def _blocks(text: str) -> list[tuple[str, str]]:
    """Split text into (heading, paragraph) pairs; headings become metadata, not chunks."""
    blocks, section = [], ""
    for raw in re.split(r"\n\s*\n", text):
        raw = raw.strip()
        if not raw:
            continue
        lines = raw.splitlines()
        m = _HEADING.match(lines[0])
        if m:
            section = m.group(1).strip()
            raw = "\n".join(lines[1:]).strip()
            if not raw:
                continue
        blocks.extend((section, piece) for piece in _split_long(raw))
    return blocks


def chunk_document(doc: Document) -> list[Chunk]:
    """Pack paragraphs up to CHUNK_WORDS, carrying OVERLAP_WORDS into the next chunk."""
    chunks: list[Chunk] = []
    parts: list[str] = []     # paragraphs collected so far
    fresh = 0                 # words in parts that are not overlap
    current = ""              # section the collected parts belong to

    def emit(keep_overlap: bool):
        nonlocal parts, fresh
        if fresh:
            text = "\n\n".join(parts)
            chunks.append(Chunk(doc.name, current, text))
            tail = text.split()[-OVERLAP_WORDS:] if keep_overlap and OVERLAP_WORDS else []
            parts = [" ".join(tail)] if tail else []
        else:
            parts = []
        fresh = 0

    for section, piece in _blocks(doc.text):
        if section != current:
            # new section: flush without overlap so topics don't bleed together
            emit(keep_overlap=False)
            current = section
        parts.append(piece)
        fresh += _words(piece)
        if fresh >= CHUNK_WORDS:
            emit(keep_overlap=True)
    emit(keep_overlap=False)
    return chunks
