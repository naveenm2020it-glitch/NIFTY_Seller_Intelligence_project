from fastapi import FastAPI, HTTPException

from app.database.session import check_database_connection

app = FastAPI(
    title="NIFTY Seller Intelligence API",
    version="0.1.0",
    description="Historical EOD NIFTY options analysis API.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "application": "nifty-seller-intelligence"}


@app.get("/health/database", tags=["system"])
def database_health_check() -> dict[str, str]:
    try:
        check_database_connection()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database connection unavailable.") from exc
    return {"status": "ok", "database": "connected"}
