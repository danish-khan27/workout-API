#!/usr/bin/env python3
from datetime import date
from app import app
from models import db, Workout, Exercise, WorkoutExercise

with app.app_context():
    # wipe in correct dependency order
    db.session.query(WorkoutExercise).delete()
    db.session.query(Workout).delete()
    db.session.query(Exercise).delete()
    db.session.commit()

    # Exercises
    squat = Exercise(name="Back Squat", category="Strength", equipment_needed=True)
    pu = Exercise(name="Push-up", category="Strength", equipment_needed=False)
    run = Exercise(name="Run", category="Cardio", equipment_needed=False)
    db.session.add_all([squat, pu, run])
    db.session.commit()

    # Workouts
    w1 = Workout(date=date(2025, 9, 1), duration_minutes=45, notes="Lower body")
    w2 = Workout(date=date(2025, 9, 3), duration_minutes=30, notes="Upper + cardio")
    db.session.add_all([w1, w2])
    db.session.commit()

    # WorkoutExercises (payload)
    db.session.add_all([
        WorkoutExercise(workout=w1, exercise=squat, reps=5, sets=5),
        WorkoutExercise(workout=w2, exercise=pu, reps=15, sets=4),
        WorkoutExercise(workout=w2, exercise=run, duration_seconds=1200),  # 20 min
    ])
    db.session.commit()

    print("🌱 Seeded!")
