from datetime import date
from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    login: str
    password: str


class FoodIn(BaseModel):
    log_date: date
    meal: str = "Snack"
    food_name: str
    serving: str = "1 serving"
    calories: float = 0
    protein_g: float = 0
    carbs_g: float = 0
    fat_g: float = 0
    notes: str = ""


class WaterIn(BaseModel):
    log_date: date
    amount_ml: int = Field(gt=0, le=10000)


class WorkoutIn(BaseModel):
    workout_date: date
    workout_name: str
    category: str = "Strength"
    duration_min: int = Field(default=0, ge=0, le=1440)
    calories_burned: int = Field(default=0, ge=0, le=10000)
    notes: str = ""


class ExerciseSetIn(BaseModel):
    exercise_name: str
    set_number: int = Field(default=1, ge=1, le=100)
    reps: int = Field(default=0, ge=0, le=1000)
    weight_lb: float = Field(default=0, ge=0, le=5000)
    distance_miles: float = Field(default=0, ge=0, le=1000)
    duration_min: float = Field(default=0, ge=0, le=1440)
    completed: bool = True


class CheckInIn(BaseModel):
    checkin_date: date
    sleep_hours: float = Field(default=0, ge=0, le=24)
    steps: int = Field(default=0, ge=0, le=200000)
    energy: int = Field(default=5, ge=1, le=10)
    stress: int = Field(default=5, ge=1, le=10)
    soreness: int = Field(default=5, ge=1, le=10)
    mood: int = Field(default=5, ge=1, le=10)
    notes: str = ""


class MeasurementIn(BaseModel):
    measurement_date: date
    weight_lb: float | None = Field(default=None, ge=0, le=2000)
    body_fat_pct: float | None = Field(default=None, ge=0, le=100)
    waist_in: float | None = Field(default=None, ge=0, le=200)
    chest_in: float | None = Field(default=None, ge=0, le=200)
    hips_in: float | None = Field(default=None, ge=0, le=200)
    arm_in: float | None = Field(default=None, ge=0, le=100)
    thigh_in: float | None = Field(default=None, ge=0, le=100)
    notes: str = ""


class GoalIn(BaseModel):
    title: str
    category: str = "Fitness"
    target_value: float = 0
    current_value: float = 0
    unit: str = ""
    target_date: date | None = None

class DeleteAccountIn(BaseModel):
    password: str
    confirm: str


class WearableMetricIn(BaseModel):
    metric_date: date
    source: str = Field(min_length=1, max_length=80)
    sleep_hours: float = Field(default=0, ge=0, le=24)
    sleep_quality: int = Field(default=5, ge=1, le=10)
    steps: int = Field(default=0, ge=0, le=200000)
    resting_hr: float = Field(default=0, ge=0, le=300)
    hrv_ms: float = Field(default=0, ge=0, le=1000)
    active_calories: float = Field(default=0, ge=0, le=20000)
    notes: str = Field(default="", max_length=1000)
