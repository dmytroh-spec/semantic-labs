"""Render the URI-to-URI part of the RDF graph as a readable PNG network."""

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".matplotlib"))

import matplotlib.pyplot as plt
import networkx as nx
from rdflib import RDF, RDFS, URIRef

from rdf_model import EX, OUTPUT, load_kyiv_graph

COLORS = {
    EX.Country: "#b8d8ba",
    EX.City: "#9ecae1",
    EX.Attraction: "#fdd0a2",
    EX.AttractionType: "#dadaeb",
    EX.TouristRoute: "#f7b6d2",
}
LAYERS = {
    EX.TouristRoute: 0,
    EX.Attraction: 1,
    EX.City: 2,
    EX.Country: 3,
    EX.AttractionType: 3,
}


def main() -> None:
    rdf_graph = load_kyiv_graph()
    graph = nx.DiGraph()
    node_colors = {}

    for subject, _, rdf_type in rdf_graph.triples((None, RDF.type, None)):
        if rdf_type in COLORS:
            label = next(rdf_graph.objects(subject, RDFS.label), subject)
            graph.add_node(subject, label=str(label), layer=LAYERS[rdf_type])
            node_colors[subject] = COLORS[rdf_type]

    # Literal values are intentionally omitted to prevent the diagram from being
    # dominated by prices, ratings, and labels instead of semantic relationships.
    visual_relations = {
        EX.locatedInCity, EX.locatedInCountry, EX.hasAttractionType,
        EX.includesAttraction, EX.nextStop,
    }
    for subject, predicate, obj in rdf_graph:
        if predicate in visual_relations and isinstance(obj, URIRef):
            graph.add_edge(subject, obj, label=predicate.rsplit("/", 1)[-1])

    labels = nx.get_node_attributes(graph, "label")
    colors = [node_colors.get(node, "#dddddd") for node in graph.nodes]
    # A layered layout exposes the route -> attraction -> city -> country path.
    position = nx.multipartite_layout(graph, subset_key="layer", align="vertical", scale=2.2)
    plt.figure(figsize=(20, 13))
    nx.draw_networkx_nodes(graph, position, node_color=colors, node_size=1050,
                           edgecolors="#455a64", linewidths=0.7)
    nx.draw_networkx_edges(graph, position, alpha=0.4, arrows=True, arrowsize=13)
    nx.draw_networkx_labels(graph, position, labels=labels, font_size=7)
    plt.title("RDF-граф туристичних ресурсів Києва", fontsize=17)
    plt.axis("off")
    plt.tight_layout()
    OUTPUT.mkdir(exist_ok=True)
    plt.savefig(OUTPUT / "kyiv_tourism_graph.png", dpi=220, bbox_inches="tight")
    plt.close()
    print(f"Візуалізація: {graph.number_of_nodes()} вузлів, {graph.number_of_edges()} ребер")


if __name__ == "__main__":
    main()

