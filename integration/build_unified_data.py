"""Create one application-ready dataset from the two laboratory projects."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab2" / "src"))

from entity_resolver import enrich_fact_ids, load_catalog  # noqa: E402
from models import FactCollection  # noqa: E402

OUTPUT = ROOT / "data" / "unified_kyiv_tourism.json"


def build() -> dict:
    catalog = load_catalog()
    facts_path = ROOT / "lab2" / "data" / "facts.json"
    facts = enrich_fact_ids(FactCollection.model_validate_json(facts_path.read_text(encoding="utf-8")))
    facts_by_attraction: dict[str, list[dict]] = {}
    for fact in facts.facts:
        for entity_id in (fact.subject_id, fact.object_id):
            if entity_id and entity_id.startswith("attraction/"):
                facts_by_attraction.setdefault(entity_id, []).append(fact.model_dump())

    attractions = []
    for attraction in catalog["attractions"]:
        entity_id = f"attraction/{attraction['id']}"
        attractions.append({
            **attraction,
            "entity_id": entity_id,
            "semantic_facts": facts_by_attraction.get(entity_id, []),
        })

    return {
        "schema_version": "1.0",
        "countries": catalog["countries"],
        "cities": catalog["cities"],
        "categories": catalog["types"],
        "attractions": attractions,
        "routes": catalog["routes"],
        "knowledge_facts": [fact.model_dump() for fact in facts.facts],
    }


def main() -> None:
    payload = build()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    linked = sum(bool(item["semantic_facts"]) for item in payload["attractions"])
    print(f"Unified dataset: {len(payload['attractions'])} attractions, "
          f"{len(payload['knowledge_facts'])} facts, {linked} linked attractions")


if __name__ == "__main__":
    main()
