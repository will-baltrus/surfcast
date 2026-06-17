#!/usr/bin/env python3
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.sqlite3"

db = SQLAlchemy(app)

# Surf spot we are collecting conditions for: Oahu, North Shore (Pipeline).
LATITUDE = 21.665
LONGITUDE = -158.053


# The database model / schema: one row per reading for the surf spot.
# Tide and wave data (height, period, direction) will come from other sources
# and can be added as more columns later.
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Integer, nullable=False)


# Fetch the current temperature, wind speed and wind direction for the surf
# spot from the Open-Meteo API.
def get_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&current=temperature_2m,wind_speed_10m,wind_direction_10m"
    )
    current = requests.get(url).json()["current"]
    return (
        current["temperature_2m"],
        current["wind_speed_10m"],
        current["wind_direction_10m"],
    )


if __name__ == "__main__":
    with app.app_context():
        # Database setup: create the table if it does not exist yet.
        db.create_all()

        # Fetch the data and store it as a new row.
        temperature, wind_speed, wind_direction = get_weather()
        new_entry = Weather(
            temperature=temperature,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
        )
        db.session.add(new_entry)
        db.session.commit()

        print(
            f"Saved reading - temp: {temperature}C, "
            f"wind: {wind_speed} km/h from {wind_direction}deg"
        )
