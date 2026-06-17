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
