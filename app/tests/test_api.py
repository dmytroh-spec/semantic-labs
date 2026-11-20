"""API contract tests."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_reports_dataset_counts(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["attractions"], 15)
        self.assertEqual(response.json()["facts"], 40)

    def test_home_page_and_assets_are_served(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Київ поруч", response.text)
        self.assertEqual(self.client.get("/static/app.js").status_code, 200)

    def test_catalog_filters_and_semantic_text_search(self):
        free = self.client.get("/api/attractions", params={"free_only": "true"}).json()
        self.assertTrue(free["items"])
        self.assertTrue(all(item["price"] == 0 for item in free["items"]))

        search = self.client.get("/api/attractions", params={"q": "Ярослав Мудрий"}).json()
        ids = {item["id"] for item in search["items"]}
        self.assertIn("saint-sophia", ids)
        self.assertIn("golden-gate", ids)

        rated = self.client.get("/api/attractions", params={"min_rating": 4.8}).json()
        self.assertTrue(rated["items"])
        self.assertTrue(all(item["rating"] >= 4.8 for item in rated["items"]))
        self.assertTrue(all(item["price"] == 0 or item["price"] >= 40 for item in rated["items"]))

    def test_attraction_detail_and_404(self):
        response = self.client.get("/api/attractions/saint-sophia")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["entity_id"], "attraction/saint-sophia")
        self.assertEqual(self.client.get("/api/attractions/unknown").status_code, 404)

    def test_routes_have_ordered_coordinates(self):
        payload = self.client.get("/api/routes").json()
        self.assertEqual(payload["count"], 6)
        for route in payload["items"]:
            positions = [stop["position"] for stop in route["stops"]]
            self.assertEqual(positions, list(range(1, len(positions) + 1)))
            self.assertTrue(all("latitude" in stop and "longitude" in stop for stop in route["stops"]))
            self.assertGreater(route["distance_km"], 0)
            self.assertGreater(route["duration_minutes"], 0)

    def test_route_detail_and_404(self):
        response = self.client.get("/api/routes/ancient-kyiv")
        self.assertEqual(response.status_code, 200)
        self.assertIn("duration_label", response.json())
        self.assertEqual(self.client.get("/api/routes/unknown").status_code, 404)


if __name__ == "__main__":
    unittest.main()
