# Surfcast

Surfcast collects surf conditions for several surf breaks on Oahu, gives each
break a surf-quality score, and ranks the breaks against each other so you can
see where to surf. It was built for my Applications in Software Architecture for
Big Data course.

## Live URL

https://surfcast-7dnb.onrender.com

## What it does

- Collects temperature, wind, wave height and wave period for a handful of Oahu
  breaks from the Open-Meteo API.
- Stores each reading in a SQLite database.
- Scores each break 0-100 from its waves, period and wind, and ranks the breaks.
- Shows the ranking on a web page with a form to look up a break's average score
  over a date range.
- Has a small JSON API and health/stats endpoints.

See `docs/report.md` for the full write-up and `docs/requirements.md` and
`docs/user_stories.md` for the requirements and stories.

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

## Collect data

The collector fetches the current conditions for each break and stores a reading.
Run it from the project root:

       python -m src.collect_weather

The first run creates the database table automatically; each run adds one reading
per break to `instance/surf.sqlite3`.

## Collect through a message queue (optional)

Instead of saving straight to the database, the collector can publish each reading
to a RabbitMQ queue, and a consumer reads the queue and saves the readings. Set
`RABBITMQ_URL` to your broker (for example a free CloudAMQP instance), then in one
terminal start the consumer:

       python -m src.consumer

and in another, run the collector:

       python -m src.collect_weather

## Run the tests

       python -m unittest discover

## Production database and scheduled collection

Locally the app uses SQLite. In production the live site can't keep SQLite data
(Render's free tier wipes the disk on restart), so it uses a hosted Postgres
database instead. The database location is read from the `SURFCAST_DATABASE_URI`
environment variable, so no code changes are needed - the web service on Render
and the collector both point at the same Postgres by setting that variable.

The collector runs on a schedule with GitHub Actions
(`.github/workflows/collect.yml`, every 3 hours) and writes to the production
Postgres using a `SURFCAST_DATABASE_URI` repository secret. It can also be run on
demand from the Actions tab.

## Endpoints

- `/` - ranked breaks and the average-score form
- `/api/breaks` - ranked breaks as JSON
- `/api/breaks/<name>/average/<start>/<end>` - average score for a break
- `/health` - health check
- `/stats` - how much data has been collected

## Roadmap

The breaks and wave data are in place. Still planned:

- More Oahu breaks.
- Tide and swell direction, which would make the score more accurate.
- Tuning the surf-quality score against real conditions.
