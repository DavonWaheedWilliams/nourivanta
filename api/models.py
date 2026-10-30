from datetime import date, datetime, timezone
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(80), default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    activity_level: Mapped[str] = mapped_column(String(40), default="Moderately active")
    calorie_target: Mapped[int] = mapped_column(Integer, default=2200)
    protein_target: Mapped[int] = mapped_column(Integer, default=150)
    carb_target: Mapped[int] = mapped_column(Integer, default=240)
    fat_target: Mapped[int] = mapped_column(Integer, default=70)
    water_target_ml: Mapped[int] = mapped_column(Integer, default=2500)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class FoodLog(Base):
    __tablename__ = "food_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    log_date: Mapped[date] = mapped_column(Date, index=True)
    meal: Mapped[str] = mapped_column(String(30))
    food_name: Mapped[str] = mapped_column(String(120))
    serving: Mapped[str] = mapped_column(String(80), default="1 serving")
    calories: Mapped[float] = mapped_column(Float, default=0)
    protein_g: Mapped[float] = mapped_column(Float, default=0)
    carbs_g: Mapped[float] = mapped_column(Float, default=0)
    fat_g: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class WaterLog(Base):
    __tablename__ = "water_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    log_date: Mapped[date] = mapped_column(Date, index=True)
    amount_ml: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    workout_date: Mapped[date] = mapped_column(Date, index=True)
    workout_name: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40), default="Strength")
    duration_min: Mapped[int] = mapped_column(Integer, default=0)
    calories_burned: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id", ondelete="CASCADE"), index=True)
    exercise_name: Mapped[str] = mapped_column(String(120))
    set_number: Mapped[int] = mapped_column(Integer, default=1)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    weight_lb: Mapped[float] = mapped_column(Float, default=0)
    distance_miles: Mapped[float] = mapped_column(Float, default=0)
    duration_min: Mapped[float] = mapped_column(Float, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)


class Measurement(Base):
    __tablename__ = "measurements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    measurement_date: Mapped[date] = mapped_column(Date, index=True)
    weight_lb: Mapped[float | None] = mapped_column(Float, nullable=True)
    body_fat_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    waist_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    chest_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    hips_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    arm_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    thigh_in: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class Goal(Base):
    __tablename__ = "goals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(40), default="Fitness")
    target_value: Mapped[float] = mapped_column(Float, default=0)
    current_value: Mapped[float] = mapped_column(Float, default=0)
    unit: Mapped[str] = mapped_column(String(30), default="")
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class DailyCheckIn(Base):
    __tablename__ = "daily_checkins"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    checkin_date: Mapped[date] = mapped_column(Date, index=True)
    sleep_hours: Mapped[float] = mapped_column(Float, default=0)
    steps: Mapped[int] = mapped_column(Integer, default=0)
    energy: Mapped[int] = mapped_column(Integer, default=5)
    stress: Mapped[int] = mapped_column(Integer, default=5)
    soreness: Mapped[int] = mapped_column(Integer, default=5)
    mood: Mapped[int] = mapped_column(Integer, default=5)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

class SecurityProfile(Base):
    __tablename__ = "security_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    recovery_code_hash: Mapped[str] = mapped_column(String(255), default="")
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    session_timeout_min: Mapped[int] = mapped_column(Integer, default=1440)
    plan_tier: Mapped[str] = mapped_column(String(30), default="Core")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class LoginEvent(Base):
    __tablename__ = "login_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    login_identifier: Mapped[str] = mapped_column(String(255), default="")
    event_time: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    client_info: Mapped[str] = mapped_column(String(300), default="NouriVanta Mobile API")


class WearableMetric(Base):
    __tablename__ = "wearable_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    metric_date: Mapped[date] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(String(80), default="Manual")
    sleep_hours: Mapped[float] = mapped_column(Float, default=0)
    sleep_quality: Mapped[int] = mapped_column(Integer, default=5)
    steps: Mapped[int] = mapped_column(Integer, default=0)
    resting_hr: Mapped[float] = mapped_column(Float, default=0)
    hrv_ms: Mapped[float] = mapped_column(Float, default=0)
    active_calories: Mapped[float] = mapped_column(Float, default=0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
