from datetime import date
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field

class ExpirySelectionMode(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"

class ConfigurationPreview(BaseModel):
    analysis_date: date
    available_expiries: list[date]
    nearest_expiry: date
    selected_expiry: date | None
    expiry_selection_mode: ExpirySelectionMode
    automatic_fallback: bool = False
    fallback_reason: str | None = None

class StartAnalysisRequest(BaseModel):
    analysis_date: date
    expiry: date | None = None
    idempotency_key: str = Field(min_length=8, max_length=128)

class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    analysis_date: date
    selected_expiry: date
    expiry_selection_mode: ExpirySelectionMode
    status: str
    config_snapshot: dict
    source_provenance: dict
    stage_results: list[dict]
    error_message: str | None = None
    created_at: str
    updated_at: str
