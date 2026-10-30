# NouriVanta Mobile API

FastAPI service for the native NouriVanta client. It reads and writes the existing NouriVanta database and does not replace the Streamlit app.

## Production changes

- Database-backed `/health` readiness check
- Existing account login with signed bearer tokens
- Wearable upsert/read endpoints using the existing `wearable_metrics` table
- Docker deployment file
- Automated pytest coverage for health, authentication and wearable upsert behavior

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r api/requirements-dev.txt
# Set DATABASE_URL and NOURIVANTA_JWT_SECRET in the environment.
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pytest -q api/tests
```

Production requires HTTPS, a strong `NOURIVANTA_JWT_SECRET`, and the same PostgreSQL `DATABASE_URL` used by NouriVanta. Keep credentials outside GitHub.
