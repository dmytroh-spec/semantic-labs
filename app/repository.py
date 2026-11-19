"""Read-only access and search over the unified tourism dataset."""

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "data" / "unified_kyiv_tourism.json"


def normalize(value: str) -> str:
    return " ".join(re.findall(r"\w+", value.casefold(), flags=re.UNICODE))


@lru_cache(maxsize=1)
def load_data() -> dict:
    return json.loads(DATASET.read_text(encoding="utf-8"))


def list_attractions(
    query: str | None = None,
    category: str | None = None,
    free_only: bool = False,
    min_rating: float | None = None,
) -> list[dict]:
    items = load_data()["attractions"]
    query_terms = set(normalize(query).split()) if query else set()
    category_key = normalize(category) if category else None
    results = []
    for item in items:
        if category_key and category_key not in {
            normalize(item["type"]), normalize(item["category"])
        }:
            continue
        if free_only and item["price"] != 0:
            continue
        if min_rating is not None and item["rating"] < min_rating:
            continue
        if query_terms:
            facts = " ".join(
                f'{fact["subject"]} {fact["object"]} {fact["evidence"]}'
                for fact in item["semantic_facts"]
            )
            searchable = normalize(" ".join([
                item["name"], *item.get("aliases", []), item["description"],
                item["category"], facts,
            ]))
            score = sum(term in searchable for term in query_terms)
            if not score:
                continue
        else:
            score = 0
        results.append({**item, "search_score": score})
    return sorted(results, key=lambda item: (-item["search_score"], -item["rating"], item["name"]))


def get_attraction(attraction_id: str) -> dict | None:
    normalized_id = attraction_id.removeprefix("attraction/")
    return next(
        (item for item in load_data()["attractions"] if item["id"] == normalized_id),
        None,
    )


def list_routes() -> list[dict]:
    data = load_data()
    attractions = {item["id"]: item for item in data["attractions"]}
    return [
        {
            **route,
            "stops": [
                {
                    "position": position,
                    "id": stop_id,
                    "entity_id": attractions[stop_id]["entity_id"],
                    "name": attractions[stop_id]["name"],
                    "latitude": attractions[stop_id]["latitude"],
                    "longitude": attractions[stop_id]["longitude"],
                }
                for position, stop_id in enumerate(route["stops"], start=1)
            ],
        }
        for route in data["routes"]
    ]
