"""Regression tests for the deterministic Lab 2 pipeline artifacts."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import CORPUS, DATA, OUTPUT
from knowledge_graph import build_graph, detect_communities
from models import FactCollection
from vector_search import VectorIndex
from corpus import build_chunks


class Lab2Tests(unittest.TestCase):
    def test_corpus_has_eight_documents(self):
        self.assertGreaterEqual(len(list(CORPUS.glob("*.txt"))), 8)

    def test_fact_schema_and_count(self):
        facts = FactCollection.model_validate_json((DATA / "facts.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(facts.facts), 30)
        self.assertGreaterEqual(len({fact.subject_type for fact in facts.facts}), 3)
        self.assertGreaterEqual(len({fact.relation for fact in facts.facts}), 4)

    def test_manual_verification_is_complete(self):
        quality = json.loads((DATA / "extraction_quality.json").read_text(encoding="utf-8"))
        self.assertEqual(quality["reviewed_count"], 20)
        self.assertIsNotNone(quality["accuracy"])

    def test_vector_search_returns_ranked_results(self):
        results = VectorIndex(build_chunks()).search("духовна спадщина Києва", top_n=3)
        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(results[0]["score"], results[-1]["score"])

    def test_graph_and_communities(self):
        graph = build_graph()
        self.assertGreaterEqual(graph.number_of_edges(), 30)
        self.assertGreaterEqual(len(detect_communities(graph)), 2)

    def test_required_outputs_exist(self):
        for name in ("knowledge_graph.png", "search_comparison.json",
                     "rag_comparison.json", "validation_report.txt"):
            self.assertTrue((OUTPUT / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
