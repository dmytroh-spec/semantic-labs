"""Build, analyze, and visualize a knowledge graph from extracted facts."""

import json
import os
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".matplotlib"))

import matplotlib.pyplot as plt
import networkx as nx

from config import DATA, OUTPUT, ensure_directories
from models import FactCollection

TYPE_COLORS = {
    "Attraction": "#f6bd60", "Person": "#84a59d", "HistoricalEvent": "#f28482",
    "District": "#90caf9", "Route": "#cdb4db", "Institution": "#a8dadc",
    "Concept": "#d9ed92",
}


def load_facts() -> FactCollection:
    return FactCollection.model_validate_json((DATA / "facts.json").read_text(encoding="utf-8"))


def build_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    for fact in load_facts().facts:
        subject_id = fact.subject_id or fact.subject
        object_id = fact.object_id or fact.object
        graph.add_node(subject_id, label=fact.subject, entity_type=fact.subject_type)
        graph.add_node(object_id, label=fact.object, entity_type=fact.object_type)
        # A DiGraph keeps the main relation readable; source IDs preserve provenance.
        graph.add_edge(subject_id, object_id, relation=fact.relation,
                       fact_id=fact.id, source=fact.source_doc)
    return graph


def detect_communities(graph: nx.DiGraph) -> list[dict]:
    # Louvain optimizes modularity on an undirected view: relation direction is
    # restored later when community edges are collected from the DiGraph.
    undirected = graph.to_undirected()
    groups = nx.community.louvain_communities(undirected, seed=42, resolution=1.0)
    communities = []
    for index, nodes in enumerate(groups, start=1):
        node_set = set(nodes)
        edges = [{"source": source, "relation": data["relation"], "target": target}
                 for source, target, data in graph.edges(data=True)
                 if source in node_set and target in node_set]
        communities.append({"community_id": index, "entities": sorted(nodes), "relations": edges})
    return communities


def visualize(graph: nx.DiGraph) -> None:
    position = nx.spring_layout(graph, seed=42, k=1.25)
    colors = [TYPE_COLORS.get(graph.nodes[node]["entity_type"], "#dddddd") for node in graph]
    plt.figure(figsize=(18, 13))
    nx.draw_networkx_nodes(graph, position, node_color=colors, node_size=950,
                           edgecolors="#455a64", linewidths=0.7)
    nx.draw_networkx_edges(graph, position, alpha=0.35, arrowsize=12)
    labels = {node: data.get("label", node) for node, data in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, position, labels=labels, font_size=6)
    plt.title("Kyiv tourism knowledge graph", fontsize=17)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(OUTPUT / "knowledge_graph.png", dpi=220, bbox_inches="tight")
    plt.close()


def run_graph_pipeline() -> tuple[nx.DiGraph, list[dict]]:
    ensure_directories()
    graph = build_graph()
    communities = detect_communities(graph)
    # Node-link JSON keeps the graph portable and preserves node/edge metadata.
    graph_payload = nx.node_link_data(graph, edges="links")
    (DATA / "knowledge_graph.json").write_text(
        json.dumps(graph_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "communities.json").write_text(
        json.dumps(communities, ensure_ascii=False, indent=2), encoding="utf-8")
    visualize(graph)
    return graph, communities


if __name__ == "__main__":
    graph, communities = run_graph_pipeline()
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"Louvain communities: {len(communities)}")

