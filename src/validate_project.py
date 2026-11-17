"""Check the measurable requirements of the laboratory assignment."""

from rdflib import OWL, RDF

from rdf_model import DATA, EX, OUTPUT, QUERIES, load_kyiv_graph


def main() -> None:
    graph = load_kyiv_graph()
    # Classes are project URIs used as objects of rdf:type statements.
    classes = {obj for _, _, obj in graph.triples((None, RDF.type, None))
               if str(obj).startswith(str(EX))}
    instances = {subject for subject, _, obj in graph.triples((None, RDF.type, None))
                 if obj in classes}
    relations = {predicate for _, predicate, obj in graph
                 if str(predicate).startswith(str(EX)) and isinstance(obj, type(next(iter(instances))))}
    query_files = sorted(QUERIES.glob("*.rq"))
    query_text = "\n".join(path.read_text(encoding="utf-8") for path in query_files)
    generated = DATA / "kyiv_graph_generated.ttl"
    final = DATA / "kyiv_graph.ttl"
    manual_change_present = generated.exists() and final.exists() and len(graph) > 0

    # These checks mirror the assignment rubric and fail the process if any
    # mandatory artifact or graph characteristic is missing.
    checks = [
        (len(graph) >= 50, f"щонайменше 50 RDF-трійок ({len(graph)})"),
        (len(classes) >= 5, f"щонайменше 5 типів сутностей ({len(classes)})"),
        (len(instances) >= 20, f"щонайменше 20 екземплярів ({len(instances)})"),
        (len(relations) >= 5, f"щонайменше 5 власних типів зв'язків ({len(relations)})"),
        ((DATA / "kyiv_graph.jsonld").exists(), "створено JSON-LD"),
        (manual_change_present and (DATA / "kyiv_manual_additions.ttl").exists(), "додано ручні Turtle-зміни"),
        (len(query_files) >= 5, f"наявні 5 SPARQL-запитів ({len(query_files)})"),
        ("FILTER" in query_text, "SPARQL використовує FILTER"),
        ("ORDER BY" in query_text, "SPARQL використовує ORDER BY"),
        ("COUNT" in query_text and "AVG" in query_text, "SPARQL використовує COUNT і AVG"),
        ("includesAttraction" in query_text and "locatedInCity" in query_text
         and "locatedInCountry" in query_text, "наявний перехід через три зв'язки"),
        (any(graph.triples((None, OWL.sameAs, None))), "наявні owl:sameAs-зв'язки з Wikidata"),
        ((OUTPUT / "kyiv_tourism_graph.png").exists(), "створено PNG-візуалізацію"),
        ((OUTPUT / "sparql_results.md").exists(), "збережено результати запитів"),
    ]
    lines = [("OK" if passed else "ПОМИЛКА") + ": " + description
             for passed, description in checks]
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "validation_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if not all(passed for passed, _ in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

