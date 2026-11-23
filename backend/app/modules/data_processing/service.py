"""Transactional persistence service for normalized historical EOD sessions."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database.models import AnalysisRun, EodIngestionBatch, Nifty50EodBar, NiftyOptionEodBar
from app.modules.data_processing.pipeline import build_session_payload

class ProcessingConflict(ValueError):
    pass
class ProcessingNotReady(ValueError):
    pass

def _now(): return datetime.now(timezone.utc)
def _canonical_hash(value): return hashlib.sha256(json.dumps(value,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def process_analysis_run(db: Session, run_id: str):
    run=db.scalar(select(AnalysisRun).where(AnalysisRun.id==run_id).with_for_update())
    if run is None: raise LookupError("Analysis run not found.")
    if run.status not in {"READY_FOR_PROCESSING","PROCESSING_FAILED"}:
        raise ProcessingNotReady(f"Analysis run must be READY_FOR_PROCESSING or PROCESSING_FAILED; current status is {run.status}.")
    payload=build_session_payload(run.analysis_date,run.selected_expiry)
    sources_hash=_canonical_hash(payload["sources"])
    existing=db.scalar(select(EodIngestionBatch).where(EodIngestionBatch.analysis_run_id==run.id))
    if existing:
        if existing.source_set_hash!=sources_hash: raise ProcessingConflict("Source set differs from the already ingested batch; refusing overwrite.")
        if existing.status=="COMPLETED": return existing,False
    batch=existing or EodIngestionBatch(id=__import__("uuid").uuid4().hex,analysis_run_id=run.id,trade_date=run.analysis_date,selected_expiry=run.selected_expiry,source_set_hash=sources_hash,status="PROCESSING",source_manifest=payload["sources"],validation_summary={},row_counts={},error_message=None)
    if existing is None: db.add(batch)
    else:
        batch.status="PROCESSING"; batch.error_message=None; batch.updated_at=_now()
    run.status="PROCESSING"
    run.stage_results=[*run.stage_results,{"stage":"NORMALIZATION","status":"SUCCEEDED","completed_at":_now().isoformat(),"details":{"option_rows":len(payload["option_bars"])}},
        {"stage":"DATA_VALIDATION","status":"SUCCEEDED","completed_at":_now().isoformat(),"details":payload["validation_summary"]}]
    try:
        db.flush()
        index_record=payload["index_bar"]
        prior_index=db.scalar(select(Nifty50EodBar).where(Nifty50EodBar.trade_date==run.analysis_date))
        if prior_index and prior_index.source_sha256!=index_record["source_sha256"]: raise ProcessingConflict("NIFTY 50 index source hash conflicts with persisted session.")
        if not prior_index:
            db.add(Nifty50EodBar(**index_record))
        for record in payload["option_bars"]:
            prior=db.scalar(select(NiftyOptionEodBar).where(NiftyOptionEodBar.trade_date==record["trade_date"],NiftyOptionEodBar.instrument_id==record["instrument_id"]))
            if prior:
                if prior.source_sha256!=record["source_sha256"]: raise ProcessingConflict(f"Source hash conflicts for NIFTY option instrument {record['instrument_id']}.")
                continue
            db.add(NiftyOptionEodBar(**record,ingestion_batch_id=batch.id))
        batch.status="COMPLETED"; batch.validation_summary=payload["validation_summary"]
        batch.row_counts={"index_rows":1,"option_rows":len(payload["option_bars"])}
        batch.completed_at=_now(); batch.error_message=None
        run.status="PROCESSED"; run.source_provenance={**(run.source_provenance or {}),"phase3_processing":{"batch_id":batch.id,"source_set_hash":sources_hash,"sources":payload["sources"],"validation":payload["validation_summary"]}}
        run.stage_results=[*run.stage_results,{"stage":"PERSISTENCE","status":"SUCCEEDED","completed_at":_now().isoformat(),"details":batch.row_counts}]
        db.commit(); db.refresh(batch); return batch,True
    except Exception as exc:
        db.rollback()
        failed_run=db.scalar(select(AnalysisRun).where(AnalysisRun.id==run_id).with_for_update())
        batch=db.scalar(select(EodIngestionBatch).where(EodIngestionBatch.analysis_run_id==run_id))
        if batch is None:
            batch=EodIngestionBatch(id=__import__("uuid").uuid4().hex,analysis_run_id=run_id,trade_date=failed_run.analysis_date,selected_expiry=failed_run.selected_expiry,source_set_hash=sources_hash,status="FAILED",source_manifest=payload["sources"],validation_summary=payload["validation_summary"],row_counts={},error_message="Persistence failed; no normalized rows were committed.")
            db.add(batch)
        else:
            batch.status="FAILED"; batch.error_message="Persistence failed; no normalized rows were committed."
        failed_run.status="PROCESSING_FAILED"
        failed_run.error_message=batch.error_message
        failed_run.stage_results=[*(failed_run.stage_results or []),{"stage":"PERSISTENCE","status":"FAILED","completed_at":_now().isoformat(),"details":{"error":batch.error_message}}]
        db.commit()
        if isinstance(exc,ProcessingConflict): raise
        if isinstance(exc,IntegrityError): raise ProcessingConflict("Unique-key conflict during persistence; verify existing ingestion state.") from exc
        raise

def get_batch_for_run(db: Session,run_id: str):
    return db.scalar(select(EodIngestionBatch).where(EodIngestionBatch.analysis_run_id==run_id))
