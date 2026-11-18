"""Generate the initial and manually extended RDF serializations."""

from rdf_model import DATA, build_kyiv_graph


def main() -> None:
    DATA.mkdir(exist_ok=True)
    # Keep the generated version to demonstrate automatic graph construction.
    initial_graph = build_kyiv_graph()
    initial_graph.serialize(DATA / "kyiv_graph_generated.ttl", format="turtle")

    # RDFLib merges triples while parsing, so the Turtle file acts as the
    # required manual extension without replacing the generated statements.
    final_graph = build_kyiv_graph()
    final_graph.parse(DATA / "kyiv_manual_additions.ttl", format="turtle")
    # Turtle is human-readable; JSON-LD demonstrates a second RDF syntax.
    final_graph.serialize(DATA / "kyiv_graph.ttl", format="turtle")
    final_graph.serialize(DATA / "kyiv_graph.jsonld", format="json-ld", indent=2)

    print(f"Початковий граф: {len(initial_graph)} трійок")
    print(f"Фінальний граф після ручних змін: {len(final_graph)} трійок")


if __name__ == "__main__":
    main()

