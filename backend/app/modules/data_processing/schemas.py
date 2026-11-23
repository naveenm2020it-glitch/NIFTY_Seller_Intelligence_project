from datetime import date,datetime
from pydantic import BaseModel,ConfigDict
class ProcessingResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:str
    analysis_run_id:str
    trade_date:date
    selected_expiry:date
    status:str
    row_counts:dict
    validation_summary:dict
    source_manifest:list
    error_message:str|None=None
    created_at:datetime
    completed_at:datetime|None=None
