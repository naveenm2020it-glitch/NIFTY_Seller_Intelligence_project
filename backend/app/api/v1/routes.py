from datetime import date
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import AnalysisRun
from app.database.session import get_db
from app.modules.user_config.archive import ArchiveError, ArchiveUnavailable, available_analysis_dates, resolve_configuration
from app.modules.user_config.orchestration import start_analysis
from app.modules.user_config.schemas import AnalysisRunResponse, ConfigurationPreview, ExpirySelectionMode, StartAnalysisRequest

router = APIRouter(prefix="/api/v1", tags=["configuration and orchestration"])

def _response(run):
    return {"id": run.id, "analysis_date": run.analysis_date, "selected_expiry": run.selected_expiry,
        "expiry_selection_mode": run.expiry_selection_mode, "status": run.status, "config_snapshot": run.config_snapshot,
        "source_provenance": run.source_provenance, "stage_results": run.stage_results, "error_message": run.error_message,
        "created_at": run.created_at.isoformat(), "updated_at": run.updated_at.isoformat()}

@router.get("/configuration/analysis-dates", response_model=list[date])
def get_analysis_dates():
    try: return available_analysis_dates()
    except ArchiveUnavailable as exc: raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ArchiveError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/configuration/resolve", response_model=ConfigurationPreview)
def preview_configuration(analysis_date: date, expiry: date | None = None):
    try: result = resolve_configuration(analysis_date, expiry)
    except ArchiveError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ConfigurationPreview(analysis_date=result.analysis_date, available_expiries=list(result.available_expiries),
        nearest_expiry=result.nearest_expiry, selected_expiry=result.selected_expiry,
        expiry_selection_mode=ExpirySelectionMode(result.expiry_selection_mode),
        automatic_fallback=result.automatic_fallback, fallback_reason=result.fallback_reason)

@router.post("/analysis-runs", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def create_analysis_run(request: StartAnalysisRequest, db: Session = Depends(get_db),
                        idempotency_header: str | None = Header(default=None, alias="Idempotency-Key")):
    if idempotency_header and idempotency_header != request.idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header must match the request body.")
    try: run, _created = start_analysis(db, request)
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    if run.status == "FAILED":
        raise HTTPException(status_code=422, detail={"message": run.error_message, "run_id": run.id,
            "status": run.status, "stage_results": run.stage_results})
    return _response(run)

@router.get("/analysis-runs/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: str, db: Session = Depends(get_db)):
    run = db.scalar(select(AnalysisRun).where(AnalysisRun.id == run_id))
    if run is None: raise HTTPException(status_code=404, detail="Analysis run not found.")
    return _response(run)
