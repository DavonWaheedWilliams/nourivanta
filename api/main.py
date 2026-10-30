from datetime import date, timedelta
import os
import requests
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from .auth import authenticate_user, current_user, make_token, verify_password
from .database import get_db
from .models import DailyCheckIn, ExerciseSet, FoodLog, Goal, Measurement, User, WaterLog, WearableMetric, WorkoutSession
from .schemas import CheckInIn, DeleteAccountIn, ExerciseSetIn, FoodIn, GoalIn, LoginIn, MeasurementIn, WaterIn, WearableMetricIn, WorkoutIn

app = FastAPI(title="NouriVanta Mobile API", version="1.0.0")
origins = [x.strip() for x in os.getenv("NOURIVANTA_CORS_ORIGINS", "*").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False if origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def dstr(value):
    return value.isoformat() if value else None


def user_json(user: User):
    return {
        "id": user.id, "username": user.username, "email": user.email,
        "display_name": user.display_name, "age": user.age, "height_cm": user.height_cm,
        "activity_level": user.activity_level, "calorie_target": user.calorie_target,
        "protein_target": user.protein_target, "carb_target": user.carb_target,
        "fat_target": user.fat_target, "water_target_ml": user.water_target_ml,
    }


def nutrition_totals(db: Session, user_id: int, day: date):
    row = db.execute(
        select(
            func.coalesce(func.sum(FoodLog.calories), 0),
            func.coalesce(func.sum(FoodLog.protein_g), 0),
            func.coalesce(func.sum(FoodLog.carbs_g), 0),
            func.coalesce(func.sum(FoodLog.fat_g), 0),
        ).where(FoodLog.user_id == user_id, FoodLog.log_date == day)
    ).one()
    water = db.scalar(select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(WaterLog.user_id == user_id, WaterLog.log_date == day)) or 0
    return {"calories": float(row[0]), "protein": float(row[1]), "carbs": float(row[2]), "fat": float(row[3]), "water": float(water)}


def readiness_score(checkin: DailyCheckIn | None, totals: dict, user: User) -> int:
    if not checkin:
        return 50
    sleep = min(100, max(0, checkin.sleep_hours / 8 * 100))
    energy = checkin.energy * 10
    mood = checkin.mood * 10
    low_stress = (11 - checkin.stress) * 10
    low_soreness = (11 - checkin.soreness) * 10
    hydration = min(100, totals["water"] / max(user.water_target_ml, 1) * 100)
    return int(round(0.25 * sleep + 0.2 * energy + 0.15 * mood + 0.15 * low_stress + 0.15 * low_soreness + 0.10 * hydration))


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database health check failed: {exc}")
    return {"ok": True, "service": "nourivanta-mobile-api", "version": "1.1.0", "database": "ready"}


@app.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user, message = authenticate_user(db, data.login, data.password)
    if not user:
        raise HTTPException(status_code=401, detail=message)
    return {"access_token": make_token(db, user.id), "token_type": "bearer", "user": user_json(user)}


@app.get("/me")
def me(user: User = Depends(current_user)):
    return user_json(user)


@app.delete("/me")
def delete_account(data: DeleteAccountIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if data.confirm.strip().upper() != "DELETE":
        raise HTTPException(400, "Type DELETE to confirm account deletion.")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Password is incorrect.")
    db.delete(user)
    db.commit()
    return {"ok": True}


@app.get("/dashboard")
def dashboard(day: date = Query(default_factory=date.today), db: Session = Depends(get_db), user: User = Depends(current_user)):
    totals = nutrition_totals(db, user.id, day)
    workouts = db.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user.id, WorkoutSession.workout_date == day)).all()
    minutes = sum(int(x.duration_min or 0) for x in workouts)
    checkin = db.scalar(select(DailyCheckIn).where(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date == day))
    latest_weight = db.scalar(select(Measurement.weight_lb).where(Measurement.user_id == user.id, Measurement.weight_lb.is_not(None)).order_by(Measurement.measurement_date.desc()).limit(1))
    recent = db.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user.id).order_by(WorkoutSession.workout_date.desc(), WorkoutSession.id.desc()).limit(5)).all()
    return {
        "date": dstr(day), "totals": totals,
        "targets": {"calories": user.calorie_target, "protein": user.protein_target, "carbs": user.carb_target, "fat": user.fat_target, "water": user.water_target_ml},
        "readiness": readiness_score(checkin, totals, user),
        "workout_count": len(workouts), "workout_minutes": minutes,
        "latest_weight_lb": latest_weight,
        "recent_workouts": [{"id": x.id, "date": dstr(x.workout_date), "name": x.workout_name, "category": x.category, "duration_min": x.duration_min} for x in recent],
    }


@app.get("/nutrition")
def list_nutrition(day: date = Query(default_factory=date.today), db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(FoodLog).where(FoodLog.user_id == user.id, FoodLog.log_date == day).order_by(FoodLog.id.desc())).all()
    return {"date": dstr(day), "totals": nutrition_totals(db, user.id, day), "items": [
        {"id": x.id, "meal": x.meal, "food_name": x.food_name, "serving": x.serving, "calories": x.calories, "protein_g": x.protein_g, "carbs_g": x.carbs_g, "fat_g": x.fat_g, "notes": x.notes}
        for x in rows
    ]}


@app.post("/nutrition")
def add_nutrition(data: FoodIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = FoodLog(user_id=user.id, **data.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id}


@app.delete("/nutrition/{food_id}")
def delete_nutrition(food_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(FoodLog).where(FoodLog.id == food_id, FoodLog.user_id == user.id))
    if not row: raise HTTPException(404, "Food log not found")
    db.delete(row); db.commit(); return {"ok": True}


@app.post("/water")
def add_water(data: WaterIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = WaterLog(user_id=user.id, **data.model_dump())
    db.add(row); db.commit(); db.refresh(row); return {"id": row.id}


@app.get("/barcode/{barcode}")
def barcode_lookup(barcode: str, user: User = Depends(current_user)):
    try:
        r = requests.get(f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json", timeout=8, headers={"User-Agent":"NouriVanta/1.0"})
        r.raise_for_status(); payload = r.json()
    except Exception as exc:
        raise HTTPException(502, f"Barcode service unavailable: {exc}")
    product = payload.get("product") or {}
    if not product: raise HTTPException(404, "Product not found")
    n = product.get("nutriments") or {}
    return {
        "barcode": barcode,
        "food_name": product.get("product_name") or product.get("generic_name") or "Scanned food",
        "serving": product.get("serving_size") or "1 serving",
        "calories": n.get("energy-kcal_serving") or n.get("energy-kcal_100g") or 0,
        "protein_g": n.get("proteins_serving") or n.get("proteins_100g") or 0,
        "carbs_g": n.get("carbohydrates_serving") or n.get("carbohydrates_100g") or 0,
        "fat_g": n.get("fat_serving") or n.get("fat_100g") or 0,
    }


@app.get("/workouts")
def list_workouts(limit: int = 40, db: Session = Depends(get_db), user: User = Depends(current_user)):
    rows = db.scalars(select(WorkoutSession).where(WorkoutSession.user_id == user.id).order_by(WorkoutSession.workout_date.desc(), WorkoutSession.id.desc()).limit(min(limit, 100))).all()
    result = []
    for w in rows:
        sets = db.scalars(select(ExerciseSet).where(ExerciseSet.session_id == w.id).order_by(ExerciseSet.id)).all()
        result.append({
            "id": w.id, "date": dstr(w.workout_date), "name": w.workout_name, "category": w.category,
            "duration_min": w.duration_min, "calories_burned": w.calories_burned, "notes": w.notes,
            "sets": [{"id": s.id, "exercise_name": s.exercise_name, "set_number": s.set_number, "reps": s.reps, "weight_lb": s.weight_lb, "distance_miles": s.distance_miles, "duration_min": s.duration_min, "completed": s.completed} for s in sets]
        })
    return result


@app.post("/workouts")
def add_workout(data: WorkoutIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = WorkoutSession(user_id=user.id, **data.model_dump())
    db.add(row); db.commit(); db.refresh(row); return {"id": row.id}


@app.post("/workouts/{workout_id}/sets")
def add_set(workout_id: int, data: ExerciseSetIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    workout = db.scalar(select(WorkoutSession).where(WorkoutSession.id == workout_id, WorkoutSession.user_id == user.id))
    if not workout: raise HTTPException(404, "Workout not found")
    row = ExerciseSet(session_id=workout.id, **data.model_dump())
    db.add(row); db.commit(); db.refresh(row); return {"id": row.id}


@app.delete("/workouts/{workout_id}/sets/{set_id}")
def delete_set(workout_id: int, set_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    workout = db.scalar(select(WorkoutSession).where(WorkoutSession.id == workout_id, WorkoutSession.user_id == user.id))
    if not workout: raise HTTPException(404, "Workout not found")
    row = db.scalar(select(ExerciseSet).where(ExerciseSet.id == set_id, ExerciseSet.session_id == workout.id))
    if not row: raise HTTPException(404, "Set not found")
    db.delete(row); db.commit(); return {"ok": True}


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(WorkoutSession).where(WorkoutSession.id == workout_id, WorkoutSession.user_id == user.id))
    if not row: raise HTTPException(404, "Workout not found")
    db.execute(delete(ExerciseSet).where(ExerciseSet.session_id == row.id)); db.delete(row); db.commit(); return {"ok": True}


@app.get("/readiness")
def readiness(days: int = 14, db: Session = Depends(get_db), user: User = Depends(current_user)):
    start = date.today() - timedelta(days=max(1, min(days, 90)) - 1)
    rows = db.scalars(select(DailyCheckIn).where(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date >= start).order_by(DailyCheckIn.checkin_date.desc())).all()
    return [{"id": x.id, "date": dstr(x.checkin_date), "sleep_hours": x.sleep_hours, "steps": x.steps, "energy": x.energy, "stress": x.stress, "soreness": x.soreness, "mood": x.mood, "notes": x.notes, "score": readiness_score(x, nutrition_totals(db, user.id, x.checkin_date), user)} for x in rows]


@app.post("/readiness")
def save_readiness(data: CheckInIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(DailyCheckIn).where(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date == data.checkin_date))
    if row:
        for k, v in data.model_dump().items(): setattr(row, k, v)
    else:
        row = DailyCheckIn(user_id=user.id, **data.model_dump()); db.add(row)
    db.commit(); db.refresh(row); return {"id": row.id}


@app.delete("/readiness/{checkin_id}")
def delete_readiness(checkin_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(DailyCheckIn).where(DailyCheckIn.id == checkin_id, DailyCheckIn.user_id == user.id))
    if not row: raise HTTPException(404, "Check-in not found")
    db.delete(row); db.commit(); return {"ok": True}


@app.get("/progress")
def progress(db: Session = Depends(get_db), user: User = Depends(current_user)):
    measurements = db.scalars(select(Measurement).where(Measurement.user_id == user.id).order_by(Measurement.measurement_date.desc()).limit(50)).all()
    goals = db.scalars(select(Goal).where(Goal.user_id == user.id).order_by(Goal.completed, Goal.id.desc())).all()
    return {
        "measurements": [{"id": x.id, "date": dstr(x.measurement_date), "weight_lb": x.weight_lb, "body_fat_pct": x.body_fat_pct, "waist_in": x.waist_in, "chest_in": x.chest_in, "hips_in": x.hips_in, "arm_in": x.arm_in, "thigh_in": x.thigh_in, "notes": x.notes} for x in measurements],
        "goals": [{"id": x.id, "title": x.title, "category": x.category, "target_value": x.target_value, "current_value": x.current_value, "unit": x.unit, "target_date": dstr(x.target_date), "completed": x.completed} for x in goals]
    }


@app.post("/measurements")
def add_measurement(data: MeasurementIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = Measurement(user_id=user.id, **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id": row.id}


@app.delete("/measurements/{measurement_id}")
def delete_measurement(measurement_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(Measurement).where(Measurement.id == measurement_id, Measurement.user_id == user.id))
    if not row: raise HTTPException(404, "Measurement not found")
    db.delete(row); db.commit(); return {"ok": True}


@app.post("/goals")
def add_goal(data: GoalIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = Goal(user_id=user.id, **data.model_dump()); db.add(row); db.commit(); db.refresh(row); return {"id": row.id}


@app.delete("/goals/{goal_id}")
def delete_goal(goal_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(select(Goal).where(Goal.id == goal_id, Goal.user_id == user.id))
    if not row: raise HTTPException(404, "Goal not found")
    db.delete(row); db.commit(); return {"ok": True}


@app.post("/wearables")
def upsert_wearable(data: WearableMetricIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    row = db.scalar(
        select(WearableMetric).where(
            WearableMetric.user_id == user.id,
            WearableMetric.metric_date == data.metric_date,
            WearableMetric.source == data.source,
        ).order_by(WearableMetric.id.desc()).limit(1)
    )
    values = data.model_dump()
    if row:
        for key, value in values.items():
            setattr(row, key, value)
    else:
        row = WearableMetric(user_id=user.id, **values)
        db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "metric_date": dstr(row.metric_date),
        "source": row.source,
        "sleep_hours": row.sleep_hours,
        "sleep_quality": row.sleep_quality,
        "steps": row.steps,
        "resting_hr": row.resting_hr,
        "hrv_ms": row.hrv_ms,
        "active_calories": row.active_calories,
        "notes": row.notes,
    }


@app.get("/wearables")
def list_wearables(days: int = Query(default=14, ge=1, le=90), db: Session = Depends(get_db), user: User = Depends(current_user)):
    cutoff = date.today() - timedelta(days=days - 1)
    rows = db.scalars(
        select(WearableMetric)
        .where(WearableMetric.user_id == user.id, WearableMetric.metric_date >= cutoff)
        .order_by(WearableMetric.metric_date.desc(), WearableMetric.id.desc())
    ).all()
    return [{
        "id": row.id,
        "metric_date": dstr(row.metric_date),
        "source": row.source,
        "sleep_hours": row.sleep_hours,
        "sleep_quality": row.sleep_quality,
        "steps": row.steps,
        "resting_hr": row.resting_hr,
        "hrv_ms": row.hrv_ms,
        "active_calories": row.active_calories,
        "notes": row.notes,
    } for row in rows]
