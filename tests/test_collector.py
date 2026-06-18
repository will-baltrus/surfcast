#!/usr/bin/env python3
import unittest
from unittest.mock import patch

from src.collect_weather import get_weather, get_waves, collect_break


# The collector calls the Open-Meteo API. We do not want the tests to depend on
# the network or on live conditions, so we mock requests.get and feed in our own
# fixed responses.
class TestCollector(unittest.TestCase):
    @patch("src.collect_weather.requests.get")
    def test_get_weather_reads_the_forecast_api(self, mock_get):
        mock_get.return_value.json.return_value = {
            "current": {
                "temperature_2m": 25.0,
                "wind_speed_10m": 10.0,
                "wind_direction_10m": 90,
            }
        }
        self.assertEqual(get_weather(21.0, -158.0), (25.0, 10.0, 90))

    @patch("src.collect_weather.requests.get")
    def test_get_waves_reads_the_marine_api(self, mock_get):
        mock_get.return_value.json.return_value = {
            "current": {"wave_height": 1.5, "wave_period": 12.0}
        }
        self.assertEqual(get_waves(21.0, -158.0), (1.5, 12.0))

    @patch("src.collect_weather.get_waves")
    @patch("src.collect_weather.get_weather")
    def test_collect_break_builds_a_reading(self, mock_weather, mock_waves):
        mock_weather.return_value = (25.0, 10.0, 90)
        mock_waves.return_value = (1.5, 12.0)
        reading = collect_break("Pipeline", 21.0, -158.0)
        self.assertEqual(reading.break_name, "Pipeline")
        self.assertEqual(reading.temperature, 25.0)
        self.assertEqual(reading.wind_speed, 10.0)
        self.assertEqual(reading.wave_height, 1.5)
        self.assertEqual(reading.wave_period, 12.0)


if __name__ == "__main__":
    unittest.main()
