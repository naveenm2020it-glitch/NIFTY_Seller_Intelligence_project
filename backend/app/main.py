from fastapi import FastAPI

app = FastAPI(
    title="NIFTY Seller Intelligence API",
    version="0.1.0",
    description="Historical EOD NIFTY options analysis API.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "application": "nifty-seller-intelligence"}
