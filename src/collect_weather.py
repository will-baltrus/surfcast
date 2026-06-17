#!/usr/bin/env python3
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///weather.sqlite3"

db = SQLAlchemy(app)


# The database model / schema: one row per temperature reading.
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)


# Fetch the current temperature (Celsius) for Boulder from the Open-Meteo API.
def get_temperature():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=40.015&longitude=-105.27&current=temperature_2m"
    )
    response = requests.get(url)
    return response.json()["current"]["temperature_2m"]


if __name__ == "__main__":
    with app.app_context():
        # Database setup: create the table if it does not exist yet.
        db.create_all()

        # Fetch the data and store it as a new row.
        current_temperature = get_temperature()
        new_entry = Weather(temperature=current_temperature)
        db.session.add(new_entry)
        db.session.commit()

        print("Saved temperature:", current_temperature)
