from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    analysis_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    selected_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_selection_mode: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    config_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    source_provenance: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    stage_results: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
