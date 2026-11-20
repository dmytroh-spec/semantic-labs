"""Regression tests for the Kyiv tourism RDF graph and its artifacts."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rdflib import OWL, RDF, URIRef, XSD
from rdflib.namespace import DCTERMS
from rdf_model import DATA, EX, QUERIES, SCHEMA, load_kyiv_graph


class TourismGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_kyiv_graph()

    def test_at_least_fifty_triples(self):
        self.assertGreaterEqual(len(self.graph), 50)

    def test_at_least_five_entity_types(self):
        classes = {obj for _, _, obj in self.graph.triples((None, RDF.type, None))
                   if str(obj).startswith(str(EX))}
        self.assertGreaterEqual(len(classes), 5)

    def test_at_least_twenty_instances(self):
        classes = {obj for _, _, obj in self.graph.triples((None, RDF.type, None))
                   if str(obj).startswith(str(EX))}
        instances = {subject for subject, _, obj in self.graph.triples((None, RDF.type, None))
                     if obj in classes}
        self.assertGreaterEqual(len(instances), 20)

    def test_prices_are_numeric(self):
        prices = list(self.graph.objects(None, EX.entryPriceUAH))
        self.assertTrue(prices)
        self.assertTrue(all(price.datatype == XSD.decimal for price in prices))

    def test_wikidata_links_exist(self):
        links = list(self.graph.triples((None, OWL.sameAs, None)))
        self.assertGreaterEqual(len(links), 1)
        self.assertTrue(all(isinstance(obj, URIRef) for _, _, obj in links))

    def test_attractions_have_application_fields(self):
        attractions = set(self.graph.subjects(RDF.type, EX.Attraction))
        self.assertTrue(attractions)
        for attraction in attractions:
            with self.subTest(attraction=attraction):
                self.assertIsNotNone(self.graph.value(attraction, DCTERMS.description))
                self.assertIsNotNone(self.graph.value(attraction, SCHEMA.latitude))
                self.assertIsNotNone(self.graph.value(attraction, SCHEMA.longitude))
                self.assertIsNotNone(self.graph.value(attraction, SCHEMA.image))
                self.assertIsNotNone(self.graph.value(attraction, SCHEMA.category))

    def test_serialization_round_trip(self):
        from rdflib import Graph
        turtle_graph = Graph().parse(DATA / "kyiv_graph.ttl", format="turtle")
        jsonld_graph = Graph().parse(DATA / "kyiv_graph.jsonld", format="json-ld")
        self.assertEqual(len(turtle_graph), len(jsonld_graph))

    def test_all_sparql_queries_execute(self):
        for path in QUERIES.glob("*.rq"):
            with self.subTest(query=path.name):
                list(self.graph.query(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
