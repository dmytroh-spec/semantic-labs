"""Load the text corpus and split documents into overlapping word chunks."""

import json
from dataclasses import asdict, dataclass

from config import CORPUS, DATA, ensure_directories


@dataclass
class Chunk:
    chunk_id: str
    document: str
    text: str


def load_documents() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8").strip()
            for path in sorted(CORPUS.glob("*.txt"))}


def split_document(name: str, text: str, size: int = 120, overlap: int = 25) -> list[Chunk]:
    """Use word windows so adjacent chunks retain shared context."""
    words = text.split()
    # The overlap reduces the chance of splitting an entity and its relation
    # across two independent chunks, which would hurt retrieval quality.
    step = size - overlap
    chunks = []
    for index, start in enumerate(range(0, len(words), step)):
        part = words[start:start + size]
        if len(part) < 25:
            break
        chunks.append(Chunk(f"{name[:-4]}-c{index + 1:02d}", name, " ".join(part)))
    return chunks


def build_chunks() -> list[Chunk]:
    chunks = [chunk for name, text in load_documents().items()
              for chunk in split_document(name, text)]
    ensure_directories()
    (DATA / "chunks.json").write_text(
        json.dumps([asdict(chunk) for chunk in chunks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return chunks


if __name__ == "__main__":
    result = build_chunks()
    print(f"Created {len(result)} chunks from {len(load_documents())} documents")

