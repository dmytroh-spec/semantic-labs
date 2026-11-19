"""Regression checks for the cross-laboratory application dataset."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integration"))

from build_unified_data import build


class UnifiedDataTests(unittest.TestCase):
    def test_all_catalog_attractions_are_complete(self):
        payload = build()
        required = {"entity_id", "category", "description", "latitude", "longitude", "image"}
        self.assertGreaterEqual(len(payload["attractions"]), 15)
        for attraction in payload["attractions"]:
            self.assertFalse(required - attraction.keys(), attraction["id"])
            self.assertTrue(attraction["entity_id"].startswith("attraction/"))

    def test_semantic_facts_are_joined_by_id(self):
        payload = build()
        by_id = {item["entity_id"]: item for item in payload["attractions"]}
        self.assertTrue(by_id["attraction/saint-sophia"]["semantic_facts"])
        self.assertTrue(by_id["attraction/kyiv-pechersk-lavra"]["semantic_facts"])


if __name__ == "__main__":
    unittest.main()
