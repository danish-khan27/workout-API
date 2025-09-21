#!/usr/bin/env python3
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate

from models import db, Workout, Exercise, WorkoutExercise
from schemas import (
    workout_schema, workouts_schema,
    exercise_schema, exercises_schema,
    workout_exercise_create_schema,
    workout_detail_schema, exercise_detail_schema
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


# --------------------------
# Error helpers
# --------------------------
def json_error(message, status=400):
    return jsonify({"error": message}), status


# --------------------------
# Workout endpoints
# --------------------------
@app.route("/workouts", methods=["GET"])
def list_workouts():
    qs = Workout.query.order_by(Workout.date.desc(), Workout.id.desc()).all()
    return jsonify(workouts_schema.dump(qs)), 200


@app.route("/workouts/<int:id>", methods=["GET"])
def get_workout(id):
    w = Workout.query.get(id)
    if not w:
        return json_error("Workout not found", 404)
    # detail includes embedded exercises + reps/sets/duration
    return jsonify(workout_detail_schema.dump(w)), 200


@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.get_json() or {}
    try:
        w = workout_schema.load(data)  # schema validations
    except Exception as err:
        return json_error(str(err), 422)

    db.session.add(w)
    db.session.commit()
    return jsonify(workout_schema.dump(w)), 201


@app.route("/workouts/<int:id>", methods=["DELETE"])
def delete_workout(id):
    w = Workout.query.get(id)
    if not w:
        return json_error("Workout not found", 404)
    db.session.delete(w)  # cascades remove WorkoutExercises (see models)
    db.session.commit()
    return make_response("", 204)


# --------------------------
# Exercise endpoints
# --------------------------
@app.route("/exercises", methods=["GET"])
def list_exercises():
    qs = Exercise.query.order_by(Exercise.name.asc()).all()
    return jsonify(exercises_schema.dump(qs)), 200


@app.route("/exercises/<int:id>", methods=["GET"])
def get_exercise(id):
    e = Exercise.query.get(id)
    if not e:
        return json_error("Exercise not found", 404)
    # detail shows workouts using that exercise
    return jsonify(exercise_detail_schema.dump(e)), 200


@app.route("/exercises", methods=["POST"])
def create_exercise():
    data = request.get_json() or {}
    try:
        e = exercise_schema.load(data)  # schema validations
    except Exception as err:
        return json_error(str(err), 422)

    db.session.add(e)
    db.session.commit()
    return jsonify(exercise_schema.dump(e)), 201


@app.route("/exercises/<int:id>", methods=["DELETE"])
def delete_exercise(id):
    e = Exercise.query.get(id)
    if not e:
        return json_error("Exercise not found", 404)
    db.session.delete(e)  # cascades delete-orphan WorkoutExercises if configured
    db.session.commit()
    return make_response("", 204)


# --------------------------
# Add exercise to workout
# --------------------------
@app.route(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises",
    methods=["POST"],
)
def add_exercise_to_workout(workout_id, exercise_id):
    w = Workout.query.get(workout_id)
    if not w:
        return json_error("Workout not found", 404)
    e = Exercise.query.get(exercise_id)
    if not e:
        return json_error("Exercise not found", 404)

    data = request.get_json() or {}
    # attach fk ids before load
    data["workout_id"] = workout_id
    data["exercise_id"] = exercise_id

    try:
        we = workout_exercise_create_schema.load(data)  # schema validations
    except Exception as err:
        return json_error(str(err), 422)

    db.session.add(we)
    db.session.commit()
    # return the workout detail so client sees updated list
    w = Workout.query.get(workout_id)
    return jsonify(workout_detail_schema.dump(w)), 201


# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)
