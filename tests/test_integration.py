#!/usr/bin/env python3
import unittest
from datetime import datetime

from src.app import app
from src.models import db, Reading


# An integration test: it exercises the web app, the database and the analyzer
# together. We seed a throwaway database (configured in tests/__init__.py), then
# call the real endpoints through the test client and check the results.
class TestApiIntegration(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(
                Reading(
                    break_name="Waikiki",
                    recorded_at=datetime(2026, 6, 10),
                    temperature=26.0,
                    wind_speed=5.0,
                    wind_direction=180,
                    wave_height=1.5,
                    wave_period=13.0,
                )
            )
            db.session.add(
                Reading(
                    break_name="Pipeline",
                    recorded_at=datetime(2026, 6, 10),
                    temperature=25.0,
                    wind_speed=5.0,
                    wind_direction=0,
                    wave_height=0.9,
                    wave_period=8.0,
                )
            )
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_api_breaks_ranks_the_better_break_first(self):
        response = self.client.get("/api/breaks")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Waikiki has bigger, longer-period waves, so it must come out on top.
        self.assertEqual(data[0]["break"], "Waikiki")
        self.assertEqual(data[0]["rank"], 1)
        self.assertGreater(data[0]["score"], data[1]["score"])

    def test_api_average_for_a_break(self):
        response = self.client.get(
            "/api/breaks/Waikiki/average/2026-06-01/2026-06-30"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["break"], "Waikiki")
        self.assertEqual(data["readings"], 1)
        self.assertGreater(data["average_score"], 0)

    def test_home_page_lists_the_breaks(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Waikiki", response.data)
        self.assertIn(b"Pipeline", response.data)

    def test_health_and_stats(self):
        self.assertEqual(self.client.get("/health").get_json()["status"], "ok")
        stats = self.client.get("/stats").get_json()
        self.assertEqual(stats["total_readings"], 2)
        self.assertEqual(stats["readings_per_break"]["Waikiki"], 1)


if __name__ == "__main__":
    unittest.main()
