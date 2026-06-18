#!/usr/bin/env python3
import json
import unittest
from unittest.mock import patch, MagicMock

from src.models import db, Reading
from src.collect_weather import publish_reading
from src.consumer import handle_message, app as consumer_app


# The producer talks to RabbitMQ. We mock the connection so the test does not
# need a running broker, and check that the right message is published.
class TestProducer(unittest.TestCase):
    @patch("src.collect_weather.connect")
    def test_publish_sends_the_reading_to_the_queue(self, mock_connect):
        channel = MagicMock()
        mock_connect.return_value.channel.return_value = channel

        reading = Reading(
            break_name="Pipeline",
            temperature=25.0,
            wind_speed=10.0,
            wind_direction=90,
            wave_height=1.5,
            wave_period=12.0,
        )
        publish_reading(reading)

        channel.basic_publish.assert_called_once()
        sent = json.loads(channel.basic_publish.call_args.kwargs["body"])
        self.assertEqual(sent["break_name"], "Pipeline")
        self.assertEqual(sent["wave_height"], 1.5)


# The consumer turns a queue message into a saved row. We call its message
# handler directly with a message and check the row lands in the database.
class TestConsumer(unittest.TestCase):
    def setUp(self):
        with consumer_app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with consumer_app.app_context():
            db.drop_all()

    def test_handle_message_saves_a_reading(self):
        body = json.dumps(
            {
                "break_name": "Waikiki",
                "temperature": 26.0,
                "wind_speed": 5.0,
                "wind_direction": 180,
                "wave_height": 1.4,
                "wave_period": 12.0,
            }
        )
        handle_message(body)
        with consumer_app.app_context():
            rows = Reading.query.all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].break_name, "Waikiki")
            self.assertEqual(rows[0].wave_height, 1.4)


if __name__ == "__main__":
    unittest.main()
