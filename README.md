# Surfcast

A tiny Flask web app for my Applications in Software Architecture for Big Data
course. It shows a form, you type something in, hit Submit, and it echoes your
text back to the screen.

## Live URL

https://surfcast-7dnb.onrender.com

## Run it locally

1. Create and activate a virtual environment:

       python3 -m venv venv
       source venv/bin/activate

2. Install the requirements:

       pip install -r requirements.txt

3. Start the app:

       flask --app src.app run

   Then open http://127.0.0.1:5000 in your browser.

## Run it the way the server does

       gunicorn src.app:app --bind 0.0.0.0:8000

   Then open http://127.0.0.1:8000 in your browser.

## Data collector

`src/collect_weather.py` fetches the current weather (temperature, wind speed,
and wind direction) for the Oahu North Shore surf break from the Open-Meteo API
and stores it in a SQLite database. Run it with:

       python src/collect_weather.py

The first run creates the table automatically; each run adds one row to
`instance/weather.sqlite3`. Tide and wave data will be added later from other
sources.

## Project goal and roadmap

The goal of Surfcast is to project surf quality for breaks on Oahu and rank
them against each other. The data collector above is the first step toward that.

Planned work (documented here, not implemented yet):

- Collect conditions for more Oahu breaks (for example Waikiki, Sunset and
  Waimea), not just Pipeline.
- Add more inputs that affect surf quality -- tide, and wave/swell height,
  period and direction -- which need data sources beyond Open-Meteo.
- Combine those inputs into a break-quality index that scores each break
  relative to the other breaks on the island.

For now the project just collects weather for the single Pipeline break, which
is enough for this assignment.
