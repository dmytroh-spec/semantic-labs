"""Build and load the RDF domain model for Kyiv tourism."""

import json
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef, XSD
from rdflib.namespace import DCTERMS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"
QUERIES = ROOT / "queries"
# EX is the project namespace for resources and custom predicates.
# Standard vocabularies are reused where possible; custom terms are used only
# when Schema.org or Dublin Core do not express the required relationship.
EX = Namespace("https://example.org/tourism/")
SCHEMA = Namespace("https://schema.org/")


def bind_namespaces(graph: Graph) -> None:
    """Register readable prefixes used in Turtle output and debug printing."""
    graph.bind("tour", EX)
    graph.bind("schema", SCHEMA)
    graph.bind("dcterms", DCTERMS)
    graph.bind("owl", OWL)
    graph.bind("rdfs", RDFS)


def make_resource_uri(kind: str, identifier: str) -> URIRef:
    """Create a stable URI instead of using anonymous RDF blank nodes."""
    return EX[f"{kind}/{identifier}"]


def add_resource(graph: Graph, uri: URIRef, rdf_class: URIRef, label: str) -> None:
    """Add the two statements shared by every domain resource."""
    # rdf:type links an individual resource to its class.
    graph.add((uri, RDF.type, rdf_class))
    # The @uk language tag distinguishes Ukrainian labels from plain strings.
    graph.add((uri, RDFS.label, Literal(label, lang="uk")))


def load_source() -> dict:
    return json.loads((DATA / "kyiv_tourism_data.json").read_text(encoding="utf-8"))


def build_kyiv_graph() -> Graph:
    """Convert the normalized JSON source into an in-memory RDF graph."""
    source = load_source()
    graph = Graph()
    bind_namespaces(graph)

    for class_name in ("Country", "City", "Attraction", "AttractionType", "TouristRoute"):
        # Declaring classes explicitly makes the schema visible inside the graph.
        graph.add((EX[class_name], RDF.type, RDFS.Class))

    for item in source["countries"]:
        uri = make_resource_uri("country", item["id"])
        add_resource(graph, uri, EX.Country, item["name"])
        if item.get("wikidata"):
            # owl:sameAs is valid here because both URIs identify the same entity.
            graph.add((uri, OWL.sameAs, URIRef(item["wikidata"])))

    for item in source["cities"]:
        uri = make_resource_uri("city", item["id"])
        add_resource(graph, uri, EX.City, item["name"])
        graph.add((uri, EX.locatedInCountry, make_resource_uri("country", item["country"])))
        # Explicit XSD datatypes allow numeric SPARQL comparisons and aggregation.
        graph.add((uri, SCHEMA.population, Literal(item["population"], datatype=XSD.integer)))
        if item.get("wikidata"):
            graph.add((uri, OWL.sameAs, URIRef(item["wikidata"])))

    for item in source["types"]:
        add_resource(graph, make_resource_uri("type", item["id"]), EX.AttractionType, item["name"])

    for item in source["attractions"]:
        uri = make_resource_uri("attraction", item["id"])
        add_resource(graph, uri, EX.Attraction, item["name"])
        graph.add((uri, EX.locatedInCity, make_resource_uri("city", item["city"])))
        graph.add((uri, EX.hasAttractionType, make_resource_uri("type", item["type"])))
        # str() preserves an exact decimal lexical form instead of a binary float.
        graph.add((uri, SCHEMA.ratingValue, Literal(str(item["rating"]), datatype=XSD.decimal)))
        graph.add((uri, EX.entryPriceUAH, Literal(str(item["price"]), datatype=XSD.decimal)))
        graph.add((uri, DCTERMS.description, Literal(item["description"], lang="uk")))
        graph.add((uri, SCHEMA.latitude, Literal(str(item["latitude"]), datatype=XSD.decimal)))
        graph.add((uri, SCHEMA.longitude, Literal(str(item["longitude"]), datatype=XSD.decimal)))
        graph.add((uri, SCHEMA.image, URIRef(item["image"])))
        graph.add((uri, SCHEMA.category, Literal(item["category"], lang="uk")))
        for alias in item.get("aliases", []):
            graph.add((uri, SCHEMA.alternateName, Literal(alias, lang="uk")))
        if item.get("wikidata"):
            graph.add((uri, OWL.sameAs, URIRef(item["wikidata"])))

    for item in source["routes"]:
        uri = make_resource_uri("route", item["id"])
        add_resource(graph, uri, EX.TouristRoute, item["name"])
        graph.add((uri, EX.recommendedSeason, Literal(item["season"])))
        for stop in item["stops"]:
            graph.add((uri, EX.includesAttraction, make_resource_uri("attraction", stop)))
        for current_stop, next_stop in zip(item["stops"], item["stops"][1:]):
            # nextStop preserves the order of attractions inside each route.
            graph.add((make_resource_uri("attraction", current_stop), EX.nextStop,
                       make_resource_uri("attraction", next_stop)))
    return graph


def load_kyiv_graph() -> Graph:
    """Load the final Turtle file used by queries, visualization, and tests."""
    graph = Graph()
    bind_namespaces(graph)
    graph.parse(DATA / "kyiv_graph.ttl", format="turtle")
    return graph

