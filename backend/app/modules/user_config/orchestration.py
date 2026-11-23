from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
import platform
import hashlib, json
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.models import AnalysisRun
from app.modules.user_config.archive import ArchiveError, resolve_configuration, validate_source_content
from app.modules.user_config.schemas import StartAnalysisRequest

def _now(): return datetime.now(timezone.utc).isoformat()
def _software_versions():
    packages = {}
    for package in ("fastapi", "SQLAlchemy", "pandas", "numpy", "scikit-learn"):
        try: packages[package] = version(package)
        except PackageNotFoundError: packages[package] = "not-installed"
    return {"application": "0.2.0", "orchestrator": "phase2-v1",
            "python": platform.python_version(), "packages": packages,
            "analytical_models": "not-implemented-in-phase-2"}
def _hash(request):
    value = {"analysis_date": request.analysis_date.isoformat(), "expiry": request.expiry.isoformat() if request.expiry else None}
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
def _stage(run, name, state, details=None):
    now = _now()
    run.stage_results = [*run.stage_results, {"stage": name, "status": state, "started_at": now, "completed_at": now, "details": details or {}}]

def start_analysis(db: Session, request: StartAnalysisRequest):
    digest = _hash(request)
    existing = db.scalar(select(AnalysisRun).where(AnalysisRun.idempotency_key == request.idempotency_key))
    if existing:
        if existing.request_hash != digest: raise ValueError("This idempotency key was already used with a different configuration.")
        return existing, False
    run = AnalysisRun(id=str(uuid4()), idempotency_key=request.idempotency_key, request_hash=digest,
        analysis_date=request.analysis_date, selected_expiry=request.expiry,
        expiry_selection_mode="MANUAL" if request.expiry else "AUTO", status="RUNNING",
        config_snapshot={"analysis_date": request.analysis_date.isoformat(), "requested_expiry": request.expiry.isoformat() if request.expiry else None,
                         "expiry_selection_mode": "MANUAL" if request.expiry else "AUTO", "preferences": {},
                         "schema_version": "phase2-config-v1", "software_versions": _software_versions()},
        source_provenance={}, stage_results=[], error_message=None)
    db.add(run)
    try: db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(AnalysisRun).where(AnalysisRun.idempotency_key == request.idempotency_key))
        if existing and existing.request_hash == digest: return existing, False
        raise ValueError("Idempotency key conflict; retry with a new key.") from None
    try:
        _stage(run, "CONFIGURATION_VALIDATION", "SUCCEEDED", {"analysis_date": request.analysis_date.isoformat()}); db.commit()
        resolved = resolve_configuration(request.analysis_date, request.expiry)
        run.selected_expiry, run.expiry_selection_mode = resolved.selected_expiry, resolved.expiry_selection_mode
        run.config_snapshot = {**run.config_snapshot, "selected_expiry": resolved.selected_expiry.isoformat(),
            "available_expiries": [x.isoformat() for x in resolved.available_expiries],
            "automatic_fallback": resolved.automatic_fallback, "fallback_reason": resolved.fallback_reason}
        _stage(run, "EXPIRY_RESOLUTION", "SUCCEEDED", {"selected_expiry": resolved.selected_expiry.isoformat(),
            "selection_mode": resolved.expiry_selection_mode, "automatic_fallback": resolved.automatic_fallback}); db.commit()
        _stage(run, "SOURCE_RESOLUTION", "SUCCEEDED", {"sources": [x.kind for x in resolved.sources]}); db.commit()
        checks = validate_source_content(resolved.sources)
        run.source_provenance = {
            "archive_root": "configured local Phase 1 archive",
            "coverage": {"analysis_date": request.analysis_date.isoformat(),
                         "required_datasets": ["fo_bhavcopy", "mii_contract", "nifty50_ohlc"],
                         "complete": True},
            "manifest_validation": {"status": "VERIFIED", "hash_algorithm": "SHA-256",
                                    "verified_file_count": len(resolved.sources)},
            "sources": [
                {"kind": x.kind, "trade_date": x.trade_date.isoformat(), "path": str(x.path), "filename": x.path.name,
                 "sha256": x.manifest_entry.get("sha256"), "bytes": x.manifest_entry.get("bytes"),
                 "source_url": x.manifest_entry.get("url"), "integrity_status": "VERIFIED"}
                for x in resolved.sources],
            "content_checks": checks}
        _stage(run, "INTEGRITY_VALIDATION", "SUCCEEDED",
               {"manifest_integrity_verified": True, "verified_file_count": len(resolved.sources),
                "required_schema_validation": "PASSED", **checks}); db.commit()
        _stage(run, "PROCESSING_HANDOFF", "SUCCEEDED", {"state": "validated inputs ready for later processing", "analytics_executed": False})
        run.status, run.error_message = "READY_FOR_PROCESSING", None
        db.commit()
    except (ArchiveError, ValueError) as exc:
        run.status, run.error_message = "FAILED", str(exc)
        _stage(run, "ORCHESTRATION", "FAILED", {"error": str(exc)}); db.commit()
    except Exception:
        db.rollback()
        failed = db.get(AnalysisRun, run.id)
        if failed:
            failed.status = "FAILED"
            failed.error_message = "Unexpected orchestration failure; inspect server logs using the run ID."
            _stage(failed, "ORCHESTRATION", "FAILED", {"error": failed.error_message}); db.commit()
        raise
    db.refresh(run)
    return run, True
