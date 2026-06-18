# Surfcast user stories

Each story has a point estimate and the tasks it was broken into. Points are a
rough size estimate (bigger number = more work).

## Story 1 - Rank the breaks (3 points)

As a surfer, I want to see the Oahu breaks ranked by surf quality so I can choose
where to surf.

- Given there are readings in the database
- When I open the home page
- Then I see the breaks listed best first, each with a score

Tasks:
- Add the Reading model (one row per break per reading).
- Find the latest reading for each break.
- Score and sort the breaks in the analyzer (`rank_breaks`).
- Show the ranked table on the home page.

## Story 2 - Show the conditions (2 points)

As a surfer, I want to see each break's wave height, period and wind so I
understand why it got its score.

Tasks:
- Store wave height and period as well as wind in each reading.
- Add those columns to the home page table.

## Story 3 - Average score over a date range (5 points)

As a surfer, I want the average score for a break between two dates so I can
judge a spot over time, not just right now.

- Given a break and a start and end date
- When I submit the form
- Then I see the average score across the readings in that range

Tasks:
- Add a form to the home page.
- Add an `/average` page route and parse the dates.
- Add an `average_score` function to the analyzer.
- Add a matching `/api/breaks/<name>/average/<start>/<end>` JSON endpoint.

## Story 4 - JSON API (3 points)

As a developer, I want the ranked breaks as JSON so I can build other things on
top of the data.

Tasks:
- Add the `/api/breaks` endpoint that returns the ranked breaks as JSON.

## Story 5 - Collect the data (5 points)

As the system, I want to collect current conditions for several breaks
automatically so the data stays fresh.

Tasks:
- List the breaks and their coordinates.
- Call the Open-Meteo forecast API for temperature and wind.
- Call the Open-Meteo marine API for wave height and period.
- Save a reading for each break.

## Story 6 - Decouple collection with a queue (8 points)

As an operator, I want collecting and storing to be separate processes joined by
a message queue, so they can run and scale on their own.

Tasks:
- Add shared RabbitMQ helpers (connection and message format).
- Make the collector publish readings to the queue when a broker is configured.
- Add a consumer that reads the queue and saves readings.
- Test the producer and consumer with a mocked broker.

## Story 7 - Monitoring (3 points)

As an operator, I want health and stats endpoints so I can tell the app is up and
see how much data it has.

Tasks:
- Add a `/health` endpoint that also checks the database.
- Add a `/stats` endpoint with reading counts and the last collection time.
- Log every request.

## Story 8 - Automated tests in CI (5 points)

As a developer, I want the tests to run automatically on every push so I catch
breakages early.

Tasks:
- Write unit tests for the analyzer.
- Write tests that mock the weather API and the message broker.
- Write integration tests that drive the app, database and analyzer together.
- Add a GitHub Actions workflow that installs the dependencies and runs the tests.
