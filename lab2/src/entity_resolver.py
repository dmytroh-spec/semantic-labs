"""Resolve Lab 2 entity labels to stable identifiers shared with Lab 1."""

import json
import re
import unicodedata
from pathlib import Path

from models import FactCollection

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "lab1" / "data" / "kyiv_tourism_data.json"


def normalize_label(value: str) -> str:
    """Normalize spelling differences without discarding Ukrainian letters."""
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    return re.sub(r"[^\w]+", " ", normalized, flags=re.UNICODE).strip()


def slugify(value: str) -> str:
    """Build a deterministic Unicode slug for entities outside the catalog."""
    return normalize_label(value).replace(" ", "-")


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def build_label_index(catalog: dict | None = None) -> dict[str, str]:
    catalog = catalog or load_catalog()
    index: dict[str, str] = {}
    for attraction in catalog["attractions"]:
        stable_id = f"attraction/{attraction['id']}"
        for label in [attraction["name"], *attraction.get("aliases", [])]:
            index[normalize_label(label)] = stable_id
    for route in catalog["routes"]:
        index[normalize_label(route["name"])] = f"route/{route['id']}"
    return index


def resolve_entity_id(label: str, entity_type: str, index: dict[str, str]) -> str:
    return index.get(normalize_label(label), f"entity/{entity_type.casefold()}/{slugify(label)}")


def enrich_fact_ids(collection: FactCollection) -> FactCollection:
    index = build_label_index()
    for fact in collection.facts:
        fact.subject_id = resolve_entity_id(fact.subject, fact.subject_type, index)
        fact.object_id = resolve_entity_id(fact.object, fact.object_type, index)
    return collection
