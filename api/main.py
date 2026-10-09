from fastapi import FastAPI
from sqlalchemy import text
from db.engine import engine

app = FastAPI(
    title="IntelliResolve API",
    version="0.1.0",
    description="Phase 1 backend foundation for IntelliResolve.",
)

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "service": "intelliresolve-api",
            "database": "connected",
            "phase": 1,
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "service": "intelliresolve-api",
            "database": "unavailable",
            "error": str(exc),
            "phase": 1,
        }

@app.get("/api/v1")
def root():
    return {
        "name": "IntelliResolve",
        "version": "0.1.0",
        "phase": 1,
        "message": "Application foundation is running.",
    }
