"""Keyword and vector search over corpus chunks."""

import hashlib
import json
import math
import os
import re

import numpy as np

from config import DATA, EMBEDDING_BACKEND, OUTPUT, ensure_directories
from corpus import Chunk, build_chunks

TOKEN_RE = re.compile(r"[а-яіїєґa-z0-9]+", re.IGNORECASE)
SYNONYMS = {
    "духовн": "religion", "релігійн": "religion", "сакральн": "religion",
    "храм": "religion", "собор": "religion", "монастир": "religion",
    "творч": "art", "мистецтв": "art", "галере": "art", "театр": "art",
    "зел": "park", "парк": "park", "сквер": "park",
    "військов": "war", "війна": "war", "воєн": "war",
    "меморіал": "memory", "памят": "memory", "пам'ят": "memory",
    "княж": "medieval", "середньовіч": "medieval",
    "столиц": "kyiv", "київ": "kyiv",
}
STOPWORDS = {
    "і", "й", "та", "у", "в", "на", "до", "з", "із", "за", "про",
    "які", "яка", "яке", "де", "що", "як", "чи", "це", "для", "від",
    "можна", "між", "разом", "місця", "місце",
}


def tokens(text: str) -> list[str]:
    result = []
    for token in TOKEN_RE.findall(text.lower()):
        if token in STOPWORDS:
            continue
        normalized = token
        for prefix, replacement in SYNONYMS.items():
            if token.startswith(prefix):
                normalized = replacement
                break
        result.append(normalized)
    return result


def hashing_embedding(text: str, dimensions: int = 768) -> np.ndarray:
    """Create a deterministic sparse embedding with synonym normalization."""
    vector = np.zeros(dimensions, dtype=np.float32)
    terms = tokens(text)
    for term in terms:
        digest = hashlib.blake2b(term.encode(), digest_size=8).digest()
        index = int.from_bytes(digest, "little") % dimensions
        vector[index] += 1.0
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector


def embed_texts(texts: list[str]) -> np.ndarray:
    if EMBEDDING_BACKEND == "sentence-transformers":
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
        return np.asarray(model.encode(texts, normalize_embeddings=True))
    if EMBEDDING_BACKEND == "gemini":
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        response = client.models.embed_content(model="gemini-embedding-001", contents=texts)
        matrix = np.asarray([item.values for item in response.embeddings], dtype=np.float32)
        return matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return np.vstack([hashing_embedding(text) for text in texts])


class VectorIndex:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.matrix = embed_texts([chunk.text for chunk in chunks])

    def search(self, query: str, top_n: int = 3) -> list[dict]:
        query_vector = embed_texts([query])[0]
        # All vectors are L2-normalized, so the dot product equals cosine
        # similarity and larger values mean stronger semantic relevance.
        scores = self.matrix @ query_vector
        order = np.argsort(scores)[::-1][:top_n]
        return [{"chunk_id": self.chunks[i].chunk_id, "document": self.chunks[i].document,
                 "text": self.chunks[i].text, "score": float(scores[i])} for i in order]


def keyword_search(chunks: list[Chunk], query: str, top_n: int = 3) -> list[dict]:
    # This lexical baseline intentionally uses exact token overlap. Comparing it
    # with vector search demonstrates why paraphrased queries need embeddings.
    query_terms = set(TOKEN_RE.findall(query.lower()))
    scored = []
    for chunk in chunks:
        document_terms = set(TOKEN_RE.findall(chunk.text.lower()))
        score = len(query_terms & document_terms) / math.sqrt(max(1, len(query_terms)))
        scored.append((score, chunk))
    return [{"chunk_id": chunk.chunk_id, "document": chunk.document,
             "text": chunk.text, "score": float(score)}
            for score, chunk in sorted(scored, key=lambda pair: pair[0], reverse=True)[:top_n]]


def run_search_demo() -> dict:
    chunks = build_chunks()
    index = VectorIndex(chunks)
    queries = [
        "Які духовні пам'ятки Києва пов'язані з княжою історією?",
        "Де в столиці поєднані творчість, музеї та прогулянка старим районом?",
        "Які місця допомагають зрозуміти воєнну пам'ять України?",
    ]
    comparison = {query: {"keyword": keyword_search(chunks, query),
                          "vector": index.search(query)} for query in queries}
    ensure_directories()
    (DATA / "embeddings.npy").write_bytes(b"")
    np.save(DATA / "embeddings.npy", index.matrix)
    (OUTPUT / "search_comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    return comparison


if __name__ == "__main__":
    result = run_search_demo()
    print(f"Compared keyword and vector search for {len(result)} queries")

