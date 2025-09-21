from marshmallow import Schema, fields, validates_schema, ValidationError, validate
from datetime import date
from models import Workout, Exercise, WorkoutExercise

# --------------------------
# Base nested serializers
# --------------------------
class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1))
    category = fields.Str(required=True, validate=validate.Length(min=1))
    equipment_needed = fields.Bool(required=True)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)


class WorkoutExerciseEmbedSchema(Schema):
    """Used inside Workout detail to show the exercise + payload."""
    id = fields.Int(dump_only=True)
    exercise = fields.Nested(ExerciseSchema)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

    @validates_schema
    def validate_workout(self, data, **kwargs):
        # schema validations mirror model constraints (defense in depth)
        if data.get("duration_minutes") is None or int(data["duration_minutes"]) < 1:
            raise ValidationError("duration_minutes must be >= 1.", "duration_minutes")
        if not isinstance(data.get("date"), date):
            raise ValidationError("date must be a valid ISO date (YYYY-MM-DD).", "date")

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)


class WorkoutDetailSchema(WorkoutSchema):
    """Workout detail includes nested workout_exercises with the exercise info."""
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseEmbedSchema))

workout_detail_schema = WorkoutDetailSchema()


class WorkoutRefSchema(Schema):
    """Small ref serializer to show workout id/date for exercise detail."""
    id = fields.Int()
    date = fields.Date()
    duration_minutes = fields.Int()

class ExerciseDetailSchema(ExerciseSchema):
    """Exercise detail shows which workouts include it (no payloads here)."""
    workouts = fields.List(fields.Nested(WorkoutRefSchema))

exercise_detail_schema = ExerciseDetailSchema()


# Creation schema for WorkoutExercise
class WorkoutExerciseCreateSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

    @validates_schema
    def validate_payload(self, data, **kwargs):
        reps = data.get("reps")
        sets_ = data.get("sets")
        duration = data.get("duration_seconds")

        # require at least one of reps/sets/duration
        if reps is None and sets_ is None and duration is None:
            raise ValidationError(
                "Provide at least one of: reps, sets, duration_seconds."
            )
        # positivity checks (schema-level)
        for key, val in (("reps", reps), ("sets", sets_), ("duration_seconds", duration)):
            if val is not None and int(val) < 1:
                raise ValidationError(f"{key} must be >= 1 when provided.", key)

workout_exercise_create_schema = WorkoutExerciseCreateSchema()
