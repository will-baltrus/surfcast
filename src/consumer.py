#!/usr/bin/env python3
"""
Reads surf readings off the RabbitMQ queue and saves them to the database.
Run the collector with RABBITMQ_URL set to put readings on the queue, and run
this consumer (also with RABBITMQ_URL set) to take them off and store them.
"""
import json

from flask import Flask

from src.models import db, init_db, Reading
from src.messaging import QUEUE_NAME, connect

app = Flask(__name__)
init_db(app)


# Turn one queue message into a saved Reading row.
def handle_message(body):
    data = json.loads(body)
    reading = Reading(
        break_name=data["break_name"],
        temperature=data["temperature"],
        wind_speed=data["wind_speed"],
        wind_direction=data["wind_direction"],
        wave_height=data["wave_height"],
        wave_period=data["wave_period"],
    )
    with app.app_context():
        db.session.add(reading)
        db.session.commit()
    return reading


# Pika calls this for every message that arrives on the queue.
def on_message(channel, method, properties, body):
    reading = handle_message(body)
    print(f"Saved {reading.break_name} from the queue")
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    with app.app_context():
        db.create_all()
    connection = connect()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)
    print("Waiting for readings. Press Ctrl+C to stop.")
    channel.start_consuming()


if __name__ == "__main__":
    main()
