from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.models import AnalysisRun, NiftyOptionEodBar, Nifty50EodBar
from app.database.session import get_db
from app.modules.data_processing.schemas import ProcessingResponse
from app.modules.data_processing.service import get_batch_for_run, process_analysis_run, ProcessingConflict, ProcessingNotReady

router=APIRouter(prefix="/api/v1",tags=["historical data processing"])

def _batch_response(batch):
    return {"id":batch.id,"analysis_run_id":batch.analysis_run_id,"trade_date":batch.trade_date,"selected_expiry":batch.selected_expiry,"status":batch.status,"row_counts":batch.row_counts,"validation_summary":batch.validation_summary,"source_manifest":batch.source_manifest,"error_message":batch.error_message,"created_at":batch.created_at,"completed_at":batch.completed_at}

@router.post("/analysis-runs/{run_id}/process",response_model=ProcessingResponse)
def process_run(run_id:str,db:Session=Depends(get_db)):
    try: batch,_created=process_analysis_run(db,run_id)
    except LookupError as exc: raise HTTPException(status_code=404,detail=str(exc)) from exc
    except ProcessingNotReady as exc: raise HTTPException(status_code=409,detail=str(exc)) from exc
    except ProcessingConflict as exc: raise HTTPException(status_code=409,detail=str(exc)) from exc
    except Exception as exc: raise HTTPException(status_code=422,detail="Historical processing failed. Inspect the analysis run status and source validation details.") from exc
    return _batch_response(batch)

@router.get("/analysis-runs/{run_id}/processing",response_model=ProcessingResponse)
def get_processing_status(run_id:str,db:Session=Depends(get_db)):
    run=db.scalar(select(AnalysisRun).where(AnalysisRun.id==run_id))
    if run is None: raise HTTPException(status_code=404,detail="Analysis run not found.")
    batch=get_batch_for_run(db,run_id)
    if batch is None: raise HTTPException(status_code=404,detail="No Phase 3 ingestion batch exists for this run.")
    return _batch_response(batch)

@router.get("/analysis-runs/{run_id}/processed-data")
def get_processed_data(run_id:str,db:Session=Depends(get_db)):
    run=db.scalar(select(AnalysisRun).where(AnalysisRun.id==run_id))
    if run is None: raise HTTPException(status_code=404,detail="Analysis run not found.")
    batch=get_batch_for_run(db,run_id)
    if batch is None or batch.status!="COMPLETED": raise HTTPException(status_code=409,detail="Historical data has not been processed successfully.")
    index_bar=db.scalar(select(Nifty50EodBar).where(Nifty50EodBar.trade_date==run.analysis_date))
    options=list(db.scalars(select(NiftyOptionEodBar).where(NiftyOptionEodBar.trade_date==run.analysis_date,NiftyOptionEodBar.expiry==run.selected_expiry).order_by(NiftyOptionEodBar.strike,NiftyOptionEodBar.option_type)))
    return {"analysis_run_id":run.id,"trade_date":run.analysis_date,"selected_expiry":run.selected_expiry,"index_bar":{"trade_date":index_bar.trade_date,"symbol":index_bar.symbol,"open":index_bar.open,"high":index_bar.high,"low":index_bar.low,"close":index_bar.close},"option_rows":[{"instrument_id":r.instrument_id,"expiry":r.expiry,"strike":r.strike,"option_type":r.option_type,"open":r.open,"high":r.high,"low":r.low,"close":r.close,"volume":r.volume,"open_interest":r.open_interest,"underlying_close":r.underlying_close,"contract_source":r.contract_source} for r in options],"validation":batch.validation_summary}
