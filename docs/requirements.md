# Surfcast requirements

## User requirements

These describe what someone using Surfcast can do.

- UR1: As a surfer, I can see the Oahu breaks ranked by surf quality so I know
  where to go.
- UR2: I can see the conditions behind each break's score (wave height, wave
  period and wind).
- UR3: I can pick a break and a date range and see its average surf score over
  that period.
- UR4: I can get the ranked breaks as JSON so other tools can use the data.

## System requirements

These describe what the system has to do and the constraints it works under.

- SR1: Collect current conditions for several Oahu breaks from a public weather
  API.
- SR2: Store each reading in a database. A SQL database (SQLite) is used because
  the readings are uniform, table-shaped rows.
- SR3: Work out a surf-quality score (0-100) for a break from its wave height,
  wave period and wind speed.
- SR4: Provide a web page (ranked report plus a form) and a REST API.
- SR5: Run in a production environment with a public URL (Render).
- SR6: Be covered by automated tests (unit, integration and tests that use mock
  objects) that run in continuous integration on every push.
- SR7: Support collecting readings through a message queue (RabbitMQ) so the
  collecting and the storing can run as separate processes.
- SR8: Expose health and stats endpoints and log requests so the running app can
  be monitored.
