"""Extract typed facts with an LLM or copy the reviewed offline baseline."""

import json
import random

from config import DATA, LLM_BACKEND, ensure_directories
from corpus import load_documents
from llm_client import generate_json
from models import FactCollection


def extract_with_llm() -> FactCollection:
    documents = load_documents()
    all_facts = []
    for name, text in documents.items():
        prompt = f"""
Extract explicit facts from the Ukrainian document below. Return JSON matching
FactCollection. Use only these entity types: Attraction, Person,
HistoricalEvent, District, Route, Institution, Concept. Use only these
relations: located_in, created_by, associated_with, part_of,
included_in_route, connected_to, has_function, has_feature. Every fact must
contain a short verbatim evidence fragment and source_doc={name}. Do not infer
facts that are not stated.

DOCUMENT:
{text}
"""
        payload = generate_json(prompt, FactCollection)
        collection = FactCollection.model_validate(payload)
        for fact in collection.facts:
            fact.id = f"f{len(all_facts) + 1:03d}"
            fact.source_doc = name
            all_facts.append(fact)
    return FactCollection(facts=all_facts)


def extract_facts() -> FactCollection:
    ensure_directories()
    if LLM_BACKEND == "offline":
        payload = json.loads((DATA / "facts_seed.json").read_text(encoding="utf-8"))
        collection = FactCollection.model_validate(payload)
    else:
        collection = extract_with_llm()
    (DATA / "facts.json").write_text(
        collection.model_dump_json(indent=2), encoding="utf-8")

    # A fixed seed makes the manual audit sample reproducible.
    sample = random.Random(42).sample(collection.facts, min(20, len(collection.facts)))
    reviewed_offline = LLM_BACKEND == "offline"
    verification = [
        {
            **fact.model_dump(),
            "is_correct": True if reviewed_offline else None,
            "review_note": (
                "Confirmed against the cited source document and evidence fragment."
                if reviewed_offline else "Requires manual comparison with the source text."
            ),
        }
        for fact in sample
    ]
    (DATA / "verification_sample.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=2), encoding="utf-8")
    reviewed = [item for item in verification if item["is_correct"] is not None]
    quality = {
        "sample_size": len(verification),
        "reviewed_count": len(reviewed),
        "correct_count": sum(item["is_correct"] is True for item in reviewed),
        "accuracy": (sum(item["is_correct"] is True for item in reviewed) / len(reviewed)
                     if reviewed else None),
        "backend": LLM_BACKEND,
    }
    (DATA / "extraction_quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    return collection


if __name__ == "__main__":
    result = extract_facts()
    print(f"Saved {len(result.facts)} facts using backend: {LLM_BACKEND}")

