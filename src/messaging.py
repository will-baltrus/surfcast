#!/usr/bin/env python3
"""
Shared RabbitMQ helpers used by the producer (the collector) and the consumer.
The connection string comes from the RABBITMQ_URL environment variable, which
points at a RabbitMQ broker (for example a free CloudAMQP instance).
"""
import os
import pika

# The queue that readings travel through.
QUEUE_NAME = "surf_readings"


# Open a connection to the RabbitMQ broker.
def connect():
    url = os.environ["RABBITMQ_URL"]
    return pika.BlockingConnection(pika.URLParameters(url))


# The fields we send over the queue for one reading.
def reading_to_dict(reading):
    return {
        "break_name": reading.break_name,
        "temperature": reading.temperature,
        "wind_speed": reading.wind_speed,
        "wind_direction": reading.wind_direction,
        "wave_height": reading.wave_height,
        "wave_period": reading.wave_period,
    }
