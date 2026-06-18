#!/usr/bin/env python3
"""
Works out a surf-quality score for a break from its conditions and ranks the
breaks against each other. These are plain functions with no database or web
code, so they are easy to test on their own.
"""


# Keep a number inside a range.
def clamp(value, low, high):
    return max(low, min(high, value))


# Score the surf at a break from 0 (flat or blown out) to 100 (as good as it
# gets). Bigger waves, longer period and lighter wind all raise the score.
# Waves matter most, then period, then wind.
def surf_quality_score(wave_height, wave_period, wind_speed):
    waves = clamp(wave_height / 3.0, 0, 1) * 40
    period = clamp(wave_period / 14.0, 0, 1) * 30
    wind = clamp(1 - wind_speed / 40.0, 0, 1) * 30
    return round(waves + period + wind)


# Score one reading row (anything with the wave and wind attributes).
def score_reading(reading):
    return surf_quality_score(
        reading.wave_height, reading.wave_period, reading.wind_speed
    )


# Sort readings best first, pairing each one with its score.
def rank_breaks(readings):
    scored = [(reading, score_reading(reading)) for reading in readings]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored


# Average score across a list of readings (0 if the list is empty).
def average_score(readings):
    if not readings:
        return 0
    return round(sum(score_reading(r) for r in readings) / len(readings))
