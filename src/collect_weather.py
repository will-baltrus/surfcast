#!/usr/bin/env python3
import os
import json

import requests
from flask import Flask

from src.models import db, init_db, Reading
from src.messaging import QUEUE_NAME, connect, reading_to_dict

app = Flask(__name__)
init_db(app)

# Surf breaks on Oahu we collect conditions for, with their coordinates.
BREAKS = {
    "Pipeline": (21.665, -158.053),
    "Sunset Beach": (21.679, -158.041),
    "Waimea Bay": (21.642, -158.066),
    "Waikiki": (21.276, -157.827),
}


# Get the current temperature and wind for a break from the Open-Meteo
# forecast API.
def get_weather(latitude, longitude):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m,wind_direction_10m"
    )
    current = requests.get(url).json()["current"]
    return (
        current["temperature_2m"],
        current["wind_speed_10m"],
        current["wind_direction_10m"],
    )


# Get the current wave height and period for a break from the Open-Meteo
# marine API.
def get_waves(latitude, longitude):
    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=wave_height,wave_period"
    )
    current = requests.get(url).json()["current"]
    return (
        current["wave_height"],
        current["wave_period"],
    )


# Fetch conditions for one break and build a Reading (not saved yet).
def collect_break(name, latitude, longitude):
    temperature, wind_speed, wind_direction = get_weather(latitude, longitude)
    wave_height, wave_period = get_waves(latitude, longitude)
    return Reading(
        break_name=name,
        temperature=temperature,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        wave_height=wave_height,
        wave_period=wave_period,
    )


# Save a reading straight to the database.
def save_reading(reading):
    db.session.add(reading)
    db.session.commit()


# Send a reading to the RabbitMQ queue instead of saving it directly. A
# consumer reads the queue and does the saving (see consumer.py).
def publish_reading(reading):
    connection = connect()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        body=json.dumps(reading_to_dict(reading)),
    )
    connection.close()


# Collect every break. If RABBITMQ_URL is set we publish each reading to the
# queue; otherwise we save it straight to the database.
def collect_all():
    use_queue = "RABBITMQ_URL" in os.environ
    for name, (latitude, longitude) in BREAKS.items():
        reading = collect_break(name, latitude, longitude)
        if use_queue:
            publish_reading(reading)
            print(f"Published {name} to the queue")
        else:
            save_reading(reading)
            print(
                f"Saved {name} - waves: {reading.wave_height}m at "
                f"{reading.wave_period}s, wind: {reading.wind_speed} km/h, "
                f"temp: {reading.temperature}C"
            )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        collect_all()
