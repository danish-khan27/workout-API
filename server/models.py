from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates
from datetime import date

db = SQLAlchemy()


# --------------------------
# Models
# --------------------------
class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    # Table constraints: unique + not null enforced by nullable=False
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    category = db.Column(db.String(80), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Many-to-many convenience via association object
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        viewonly=True,
        back_populates="exercises",
    )

    # -------- Model validations --------
    @validates("name")
    def validate_name(self, _, value):
        if not value or not value.strip():
            raise ValueError("Exercise.name is required.")
        return value.strip()

    @validates("category")
    def validate_category(self, _, value):
        if not value or not value.strip():
            raise ValueError("Exercise.category is required.")
        return value.strip()

    def __repr__(self):
        return f"<Exercise {self.id}, {self.name}, {self.category}, equipment={self.equipment_needed}>"


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Table constraints: positive duration
    __table_args__ = (
        CheckConstraint("duration_minutes >= 1", name="ck_workout_duration_pos"),
    )

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="WorkoutExercise.id",
    )

    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        viewonly=True,
        back_populates="workouts",
    )

    # -------- Model validations --------
    @validates("date")
    def validate_date(self, _, value):
        if not isinstance(value, date):
            raise ValueError("Workout.date must be a date.")
        # allow future dates? up to you; we'll allow any date
        return value

    @validates("duration_minutes")
    def validate_duration(self, _, value):
        if value is None or int(value) < 1:
            raise ValueError("Workout.duration_minutes must be >= 1.")
        return int(value)

    def __repr__(self):
        return f"<Workout {self.id}, {self.date}, {self.duration_minutes}m>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional details — allow NULL but constrain positive values when present.
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        # A given workout cannot have duplicate exercise rows with same reps/sets/duration payload.
        # (You can simplify to UniqueConstraint(workout_id, exercise_id) if you want strict uniqueness.)
        UniqueConstraint(
            "workout_id", "exercise_id", "reps", "sets", "duration_seconds",
            name="uq_we_payload"
        ),
        CheckConstraint("reps IS NULL OR reps >= 1", name="ck_we_reps_pos"),
        CheckConstraint("sets IS NULL OR sets >= 1", name="ck_we_sets_pos"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds >= 1",
            name="ck_we_duration_pos",
        ),
    )

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    # -------- Model validations --------
    @validates("reps", "sets", "duration_seconds")
    def validate_numbers(self, key, value):
        if value is None:
            return None
        try:
            v = int(value)
        except Exception:
            raise ValueError(f"{key} must be an integer or null.")
        if v < 1:
            raise ValueError(f"{key} must be >= 1 when provided.")
        return v

    def __repr__(self):
        payload = f"reps={self.reps}, sets={self.sets}, duration={self.duration_seconds}"
        return f"<WE id={self.id} workout={self.workout_id} exercise={self.exercise_id} {payload}>"
