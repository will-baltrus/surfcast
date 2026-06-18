#!/usr/bin/env python3
import logging
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template_string

from src.models import db, init_db, Reading
from src.analyzer import rank_breaks, average_score

app = Flask(__name__)
init_db(app)

# Log every request so we can see what is happening in production.
logging.basicConfig(level=logging.INFO)


@app.after_request
def log_request(response):
    app.logger.info("%s %s -> %s", request.method, request.path, response.status_code)
    return response


# Make sure the table exists when the app starts (the database is empty on a
# fresh deploy until the collector has run).
with app.app_context():
    db.create_all()


# The most recent reading for each break.
def latest_readings():
    readings = Reading.query.order_by(Reading.recorded_at.desc()).all()
    latest = {}
    for reading in readings:
        if reading.break_name not in latest:
            latest[reading.break_name] = reading
    return list(latest.values())


# Turn a "YYYY-MM-DD" string into a date, or None if it cannot be read.
def parse_date(text):
    try:
        return datetime.strptime(text, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


# Readings for one break between two dates (either date may be missing).
def readings_for_break_between(name, start, end):
    query = Reading.query.filter(Reading.break_name == name)
    start_date = parse_date(start)
    end_date = parse_date(end)
    if start_date:
        query = query.filter(Reading.recorded_at >= start_date)
    if end_date:
        # Add a day so the whole end date is included.
        query = query.filter(Reading.recorded_at < end_date + timedelta(days=1))
    return query.all()


HOME_PAGE = """
<!doctype html>
<title>Surfcast</title>
<h1>Surfcast - Oahu surf quality</h1>
<p>Breaks ranked by surf quality right now (higher is better).</p>
<table border="1" cellpadding="6">
  <tr>
    <th>Rank</th><th>Break</th><th>Score</th>
    <th>Wave (m)</th><th>Period (s)</th><th>Wind (km/h)</th>
  </tr>
  {% for reading, score in ranked %}
  <tr>
    <td>{{ loop.index }}</td>
    <td>{{ reading.break_name }}</td>
    <td>{{ score }}</td>
    <td>{{ reading.wave_height }}</td>
    <td>{{ reading.wave_period }}</td>
    <td>{{ reading.wind_speed }}</td>
  </tr>
  {% endfor %}
</table>
{% if not ranked %}
<p>No readings yet. Run the collector to gather some.</p>
{% endif %}

<h2>Average score for a break</h2>
<form action="/average" method="get">
  <input name="break_name" placeholder="Pipeline">
  <input name="start" placeholder="2026-06-01">
  <input name="end" placeholder="2026-06-30">
  <input type="submit" value="Show average">
</form>
"""

AVERAGE_PAGE = """
<!doctype html>
<title>Surfcast - average</title>
<h1>Average score for {{ name }}</h1>
<p>From {{ start }} to {{ end }}: average score
   <strong>{{ avg }}</strong> across {{ count }} reading(s).</p>
<p><a href="/">Back</a></p>
"""


@app.route("/")
def home():
    ranked = rank_breaks(latest_readings())
    return render_template_string(HOME_PAGE, ranked=ranked)


@app.route("/average")
def average_page():
    name = request.args.get("break_name", "")
    start = request.args.get("start", "")
    end = request.args.get("end", "")
    readings = readings_for_break_between(name, start, end)
    return render_template_string(
        AVERAGE_PAGE,
        name=name,
        start=start,
        end=end,
        avg=average_score(readings),
        count=len(readings),
    )


# REST API: the ranked breaks as JSON.
@app.route("/api/breaks")
def api_breaks():
    ranked = rank_breaks(latest_readings())
    data = []
    for rank, (reading, score) in enumerate(ranked, start=1):
        data.append(
            {
                "rank": rank,
                "break": reading.break_name,
                "score": score,
                "wave_height": reading.wave_height,
                "wave_period": reading.wave_period,
                "wind_speed": reading.wind_speed,
                "recorded_at": reading.recorded_at.isoformat(),
            }
        )
    return jsonify(data)


# REST API: the average score for a break over a date range.
@app.route("/api/breaks/<name>/average/<start>/<end>")
def api_average(name, start, end):
    readings = readings_for_break_between(name, start, end)
    return jsonify(
        {
            "break": name,
            "start": start,
            "end": end,
            "readings": len(readings),
            "average_score": average_score(readings),
        }
    )


# Health check for uptime monitoring. Also confirms the database is reachable.
@app.route("/health")
def health():
    try:
        Reading.query.first()
        return jsonify({"status": "ok"})
    except Exception:
        app.logger.exception("health check failed")
        return jsonify({"status": "error"}), 500


# Instrumentation: how much data we have collected and when.
@app.route("/stats")
def stats():
    readings = Reading.query.all()
    per_break = {}
    for reading in readings:
        per_break[reading.break_name] = per_break.get(reading.break_name, 0) + 1
    latest = Reading.query.order_by(Reading.recorded_at.desc()).first()
    return jsonify(
        {
            "total_readings": len(readings),
            "readings_per_break": per_break,
            "last_collected_at": latest.recorded_at.isoformat() if latest else None,
        }
    )
