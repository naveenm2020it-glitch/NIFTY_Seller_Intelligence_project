from datetime import date, datetime, timezone
from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Index, JSON, String, Text, UniqueConstraint
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

class EodIngestionBatch(Base):
    __tablename__ = "eod_ingestion_batches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    analysis_run_id: Mapped[str] = mapped_column(String(36), ForeignKey("analysis_runs.id", ondelete="RESTRICT"), nullable=False, unique=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    selected_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    source_set_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    source_manifest: Mapped[list] = mapped_column(JSON, nullable=False)
    validation_summary: Mapped[dict] = mapped_column(JSON, nullable=False)
    row_counts: Mapped[dict] = mapped_column(JSON, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Nifty50EodBar(Base):
    __tablename__ = "nifty50_eod_bars"
    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="NIFTY 50")
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

class NiftyOptionEodBar(Base):
    __tablename__ = "nifty_option_eod_bars"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(16), nullable=False, default="NIFTY")
    instrument_id: Mapped[str] = mapped_column(String(32), nullable=False)
    expiry: Mapped[date] = mapped_column(Date, nullable=False)
    strike: Mapped[float] = mapped_column(Float, nullable=False)
    option_type: Mapped[str] = mapped_column(String(2), nullable=False)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    open_interest: Mapped[int] = mapped_column(BigInteger, nullable=False)
    underlying_close: Mapped[float] = mapped_column(Float, nullable=False)
    contract_source: Mapped[str] = mapped_column(String(40), nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    ingestion_batch_id: Mapped[str] = mapped_column(String(36), ForeignKey("eod_ingestion_batches.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (
        UniqueConstraint("trade_date", "instrument_id", name="uq_nifty_option_eod_trade_instrument"),
        Index("ix_nifty_option_eod_expiry_strike", "expiry", "strike"),
        Index("ix_nifty_option_eod_batch", "ingestion_batch_id"),
    )
