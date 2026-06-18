#!/usr/bin/env python3
import unittest

from src.analyzer import surf_quality_score, rank_breaks, average_score


# A tiny stand-in for a Reading row, with only the fields the analyzer reads.
class FakeReading:
    def __init__(self, break_name, wave_height, wave_period, wind_speed):
        self.break_name = break_name
        self.wave_height = wave_height
        self.wave_period = wave_period
        self.wind_speed = wind_speed


class TestSurfQualityScore(unittest.TestCase):
    def test_flat_and_windy_scores_zero(self):
        # No waves, no period and wind well over the cap.
        self.assertEqual(surf_quality_score(0, 0, 50), 0)

    def test_perfect_conditions_score_100(self):
        # Big, long-period swell with no wind maxes out every part.
        self.assertEqual(surf_quality_score(3, 14, 0), 100)

    def test_values_past_the_caps_do_not_score_above_100(self):
        self.assertEqual(surf_quality_score(10, 30, 0), 100)

    def test_middle_conditions(self):
        # 1.5m / 7s / 20km/h -> 20 + 15 + 15 = 50.
        self.assertEqual(surf_quality_score(1.5, 7, 20), 50)


class TestRankAndAverage(unittest.TestCase):
    def setUp(self):
        self.readings = [
            FakeReading("Pipeline", 0.9, 8, 5),
            FakeReading("Waikiki", 1.5, 13, 5),
        ]

    def test_rank_puts_the_best_break_first(self):
        ranked = rank_breaks(self.readings)
        self.assertEqual(ranked[0][0].break_name, "Waikiki")

    def test_average_of_no_readings_is_zero(self):
        self.assertEqual(average_score([]), 0)

    def test_average_matches_the_mean_of_the_scores(self):
        scores = [
            surf_quality_score(r.wave_height, r.wave_period, r.wind_speed)
            for r in self.readings
        ]
        expected = round(sum(scores) / len(scores))
        self.assertEqual(average_score(self.readings), expected)


if __name__ == "__main__":
    unittest.main()
