import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("nourivanta_test.db")
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["NOURIVANTA_JWT_SECRET"] = "test-secret-0123456789-0123456789-0123456789"

try:
    import bcrypt
except ModuleNotFoundError:
    import hashlib
    import types
    import sys

    bcrypt = types.ModuleType("bcrypt")
    bcrypt.gensalt = lambda: b"test-salt"
    bcrypt.hashpw = lambda password, salt: b"stub$" + hashlib.sha256(password).hexdigest().encode("ascii")
    bcrypt.checkpw = lambda password, hashed: hashed == bcrypt.hashpw(password, b"test-salt")
    sys.modules["bcrypt"] = bcrypt

from fastapi.testclient import TestClient

from api.database import Base, SessionLocal, engine
from api.main import app
from api.models import User

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def seed_user():
    with SessionLocal() as db:
        existing = db.query(User).filter(User.username == "mobiletest").first()
        if existing:
            return existing.id
        row = User(
            username="mobiletest",
            email="mobiletest@example.com",
            password_hash=bcrypt.hashpw(b"StrongPass123!", bcrypt.gensalt()).decode("utf-8"),
            display_name="Mobile Test",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row.id


def auth_headers():
    seed_user()
    response = client.post("/auth/login", json={"login": "mobiletest", "password": "StrongPass123!"})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_checks_database():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["database"] == "ready"


def test_invalid_login_is_rejected():
    seed_user()
    response = client.post("/auth/login", json={"login": "mobiletest", "password": "wrong"})
    assert response.status_code == 401


def test_authenticated_profile():
    response = client.get("/me", headers=auth_headers())
    assert response.status_code == 200
    assert response.json()["username"] == "mobiletest"


def test_wearable_requires_authentication():
    response = client.get("/wearables")
    assert response.status_code == 401


def test_wearable_upsert_and_readback():
    headers = auth_headers()
    payload = {
        "metric_date": "2026-10-30",
        "source": "Health Connect",
        "sleep_hours": 7.4,
        "sleep_quality": 5,
        "steps": 8421,
        "resting_hr": 61,
        "hrv_ms": 43.2,
        "active_calories": 512.5,
        "notes": "Foreground device sync",
    }
    first = client.post("/wearables", json=payload, headers=headers)
    assert first.status_code == 200, first.text
    first_id = first.json()["id"]

    payload["steps"] = 9000
    second = client.post("/wearables", json=payload, headers=headers)
    assert second.status_code == 200, second.text
    assert second.json()["id"] == first_id
    assert second.json()["steps"] == 9000

    readback = client.get("/wearables?days=30", headers=headers)
    assert readback.status_code == 200
    matching = [x for x in readback.json() if x["source"] == "Health Connect" and x["metric_date"] == "2026-10-30"]
    assert len(matching) == 1
    assert matching[0]["steps"] == 9000
