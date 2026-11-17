"""Audit the measurable requirements of the second laboratory assignment."""

import json

import networkx as nx

from config import CORPUS, DATA, OUTPUT
from models import FactCollection


def validate() -> list[tuple[bool, str]]:
    # The audit mirrors the measurable thresholds stated in the assignment.
    documents = list(CORPUS.glob("*.txt"))
    facts = FactCollection.model_validate_json((DATA / "facts.json").read_text(encoding="utf-8"))
    entity_types = {fact.subject_type for fact in facts.facts} | {fact.object_type for fact in facts.facts}
    relation_types = {fact.relation for fact in facts.facts}
    verification = json.loads((DATA / "verification_sample.json").read_text(encoding="utf-8"))
    quality = json.loads((DATA / "extraction_quality.json").read_text(encoding="utf-8"))
    questions = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
    search = json.loads((OUTPUT / "search_comparison.json").read_text(encoding="utf-8"))
    graph_data = json.loads((DATA / "knowledge_graph.json").read_text(encoding="utf-8"))
    graph = nx.node_link_graph(graph_data, edges="links")
    communities = json.loads((DATA / "communities.json").read_text(encoding="utf-8"))

    return [
        (len(documents) >= 8, f"at least 8 corpus documents ({len(documents)})"),
        (len(questions["single_document"]) >= 3, "at least 3 single-document questions"),
        (len(questions["multi_document"]) >= 2, "at least 2 synthesis questions"),
        (len(entity_types) >= 3, f"at least 3 entity types ({len(entity_types)})"),
        (len(relation_types) >= 4, f"at least 4 relation types ({len(relation_types)})"),
        (len(facts.facts) >= 30, f"at least 30 extracted facts ({len(facts.facts)})"),
        (len(verification) == 20, "20-fact manual verification sample"),
        (quality["reviewed_count"] == 20 and quality["accuracy"] is not None,
         f"fact verification accuracy recorded ({quality['accuracy']:.0%})"),
        (len(search) >= 3, f"at least 3 search queries ({len(search)})"),
        (all("keyword" in item and "vector" in item for item in search.values()),
         "keyword and vector results saved"),
        (graph.number_of_nodes() > 0 and graph.number_of_edges() >= 30,
         f"knowledge graph created ({graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges)"),
        (len(communities) >= 2, f"Louvain communities detected ({len(communities)})"),
        ((OUTPUT / "knowledge_graph.png").exists(), "knowledge graph visualization created"),
        ((OUTPUT / "rag_comparison.json").exists(), "GraphRAG and vector-RAG compared"),
    ]


def main() -> None:
    checks = validate()
    lines = [("OK" if passed else "ERROR") + ": " + message for passed, message in checks]
    (OUTPUT / "validation_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if not all(passed for passed, _ in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

