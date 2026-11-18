"""Enrich local owl:sameAs resources with labels and coordinates from Wikidata."""

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from rdflib import OWL, RDFS

from rdf_model import OUTPUT, load_kyiv_graph


def main() -> None:
    graph = load_kyiv_graph()
    local_items = []
    # owl:sameAs supplies the join key between the local and external graphs.
    for local_uri, _, wikidata_uri in graph.triples((None, OWL.sameAs, None)):
        labels = list(graph.objects(local_uri, RDFS.label))
        if labels:
            local_items.append({
                "local_uri": str(local_uri),
                "local_label": str(labels[0]),
                "wikidata_uri": str(wikidata_uri),
                "qid": str(wikidata_uri).rsplit("/", 1)[-1],
            })

    # VALUES sends all known QIDs in one SPARQL request instead of one request
    # per attraction, which is faster and friendlier to the public endpoint.
    values = " ".join(f"wd:{item['qid']}" for item in local_items)
    query = f"""
SELECT ?item ?itemLabel ?coordinate WHERE {{
  VALUES ?item {{ {values} }}
  OPTIONAL {{ ?item wdt:P625 ?coordinate . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "uk,en". }}
}}
"""
    endpoint = "https://query.wikidata.org/sparql?" + urlencode({"query": query, "format": "json"})
    request = Request(endpoint, headers={"User-Agent": "semantic-labs-tourism/1.0"})
    OUTPUT.mkdir(exist_ok=True)
    try:
        with urlopen(request, timeout=30) as response:
            external = json.load(response)["results"]["bindings"]
        by_uri = {row["item"]["value"]: row for row in external}
        for item in local_items:
            row = by_uri.get(item["wikidata_uri"], {})
            item["wikidata_label"] = row.get("itemLabel", {}).get("value")
            item["coordinate"] = row.get("coordinate", {}).get("value")
        status = "success"
        print(f"Отримано {len(external)} записів із Wikidata")
    except Exception as error:
        # Network access is optional: the local RDF graph remains usable offline.
        status = "unavailable"
        print(f"Wikidata недоступна: {error}")
    payload = {"status": status, "items": local_items}
    (OUTPUT / "wikidata_kyiv.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

