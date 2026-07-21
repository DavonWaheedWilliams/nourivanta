# NouriVolt

Streamlit fitness, nutrition, workout, progress, readiness, food-photo, and barcode tracking app.

## Required repository files

- `app.py`
- `vision_services.py`
- `requirements.txt`
- `.streamlit/config.toml`

## Streamlit Community Cloud secrets

Add these in App settings > Secrets. Do not commit them to GitHub.

```toml
DATABASE_URL = "your Neon PostgreSQL connection string"
OPENAI_API_KEY = "your OpenAI API key"
```

The app uses local SQLite only when `DATABASE_URL` is absent.
