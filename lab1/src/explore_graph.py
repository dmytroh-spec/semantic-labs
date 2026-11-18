"""Print representative triples and inspect one selected RDF resource."""

from rdf_model import load_kyiv_graph, make_resource_uri


def main() -> None:
    graph = load_kyiv_graph()
    subject = make_resource_uri("attraction", "saint-sophia")
    print(f"Усього трійок: {len(graph)}")
    print("\nПерші 10 трійок:")
    for index, triple in enumerate(graph):
        if index == 10:
            break
        print("  " + " | ".join(value.n3(graph.namespace_manager) for value in triple))

    print("\nУсі властивості ресурсу «Софійський собор»:")
    for _, predicate, obj in graph.triples((subject, None, None)):
        print(f"  {predicate.n3(graph.namespace_manager)} | {obj.n3(graph.namespace_manager)}")

    print("\nТрійки, де ресурс є суб'єктом або об'єктом:")
    # Searching both positions shows outgoing and incoming graph relationships.
    related = set(graph.triples((subject, None, None))) | set(graph.triples((None, None, subject)))
    for triple in related:
        print("  " + " | ".join(value.n3(graph.namespace_manager) for value in triple))


if __name__ == "__main__":
    main()

