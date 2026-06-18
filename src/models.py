#!/usr/bin/env python3
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Shared database object. The collector, the consumer and the web app all import
# this same db and Reading model so they read and write the same database.
db = SQLAlchemy()

# Absolute path to the SQLite file, worked out from this file's location, so the
# collector, consumer and web app all use the same database no matter which
# folder they are started from.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INSTANCE_DIR = os.path.join(_BASE_DIR, "instance")
DB_URI = "sqlite:///" + os.path.join(_INSTANCE_DIR, "surf.sqlite3")


# Point a Flask app at the shared database. The location can be overridden with
# the SURFCAST_DATABASE_URI environment variable, which the tests use to run
# against a throwaway database.
def init_db(app):
    os.makedirs(_INSTANCE_DIR, exist_ok=True)
    # `or DB_URI` so a missing OR blank value both fall back to local SQLite.
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SURFCAST_DATABASE_URI") or DB_URI
    db.init_app(app)


# One row per reading for one surf break at one point in time.
# The surf-quality score is not stored here -- it is worked out from these
# numbers by the analyzer, so the analyzer can be tested on its own.
class Reading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    break_name = db.Column(db.String, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_direction = db.Column(db.Integer, nullable=False)
    wave_height = db.Column(db.Float, nullable=False)
    wave_period = db.Column(db.Float, nullable=False)
