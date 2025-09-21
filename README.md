# Workout API (Flask + SQLAlchemy + Marshmallow)

A backend for tracking workouts and exercises.

## Quickstart

pipenv install
pipenv shell
cd server
export FLASK_APP=app.py && export FLASK_RUN_PORT=5555
flask db upgrade
python seed.py
flask run