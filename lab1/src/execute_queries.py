"""Execute every stored SPARQL query and save reproducible Markdown results."""

from rdf_model import OUTPUT, QUERIES, load_kyiv_graph


def markdown_table(headers, rows):
    result = ["| " + " | ".join(headers) + " |",
              "| " + " | ".join("---" for _ in headers) + " |"]
    result.extend("| " + " | ".join(row) + " |" for row in rows)
    return result


def main() -> None:
    graph = load_kyiv_graph()
    OUTPUT.mkdir(exist_ok=True)
    report = ["# Результати SPARQL-запитів", ""]
    # Query logic is stored in .rq files so it can be reviewed independently.
    for query_path in sorted(QUERIES.glob("*.rq")):
        result = graph.query(query_path.read_text(encoding="utf-8"))
        headers = [str(variable) for variable in result.vars]
        rows = [[str(value) if value is not None else "" for value in row] for row in result]
        report.extend([f"## {query_path.stem}", ""])
        report.extend(markdown_table(headers, rows))
        report.append("")
        print(f"{query_path.name}: {len(rows)} результатів")
    (OUTPUT / "sparql_results.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    main()

