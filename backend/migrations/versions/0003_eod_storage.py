"""Phase 3 normalized EOD storage and ingestion audit trail."""
from alembic import op
import sqlalchemy as sa
revision="0003_eod_storage"
down_revision="0002_analysis_runs"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table("eod_ingestion_batches",
        sa.Column("id",sa.String(36),primary_key=True),
        sa.Column("analysis_run_id",sa.String(36),sa.ForeignKey("analysis_runs.id",ondelete="RESTRICT"),nullable=False,unique=True),
        sa.Column("trade_date",sa.Date,nullable=False),sa.Column("selected_expiry",sa.Date,nullable=False),
        sa.Column("source_set_hash",sa.String(64),nullable=False),sa.Column("status",sa.String(24),nullable=False),
        sa.Column("source_manifest",sa.JSON,nullable=False),sa.Column("validation_summary",sa.JSON,nullable=False),
        sa.Column("row_counts",sa.JSON,nullable=False),sa.Column("error_message",sa.Text),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("updated_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("completed_at",sa.DateTime(timezone=True)))
    op.create_index("ix_eod_ingestion_batches_trade_date","eod_ingestion_batches",["trade_date"])
    op.create_index("ix_eod_ingestion_batches_status","eod_ingestion_batches",["status"])
    op.create_table("nifty50_eod_bars",
        sa.Column("trade_date",sa.Date,primary_key=True),sa.Column("symbol",sa.String(16),nullable=False),
        sa.Column("open",sa.Float,nullable=False),sa.Column("high",sa.Float,nullable=False),sa.Column("low",sa.Float,nullable=False),sa.Column("close",sa.Float,nullable=False),
        sa.Column("source_sha256",sa.String(64),nullable=False),sa.Column("source_filename",sa.String(255),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()))
    op.create_table("nifty_option_eod_bars",
        sa.Column("id",sa.BigInteger().with_variant(sa.Integer,"sqlite"),primary_key=True,autoincrement=True),
        sa.Column("trade_date",sa.Date,nullable=False),sa.Column("symbol",sa.String(16),nullable=False),
        sa.Column("instrument_id",sa.String(32),nullable=False),sa.Column("expiry",sa.Date,nullable=False),
        sa.Column("strike",sa.Float,nullable=False),sa.Column("option_type",sa.String(2),nullable=False),
        sa.Column("open",sa.Float,nullable=False),sa.Column("high",sa.Float,nullable=False),sa.Column("low",sa.Float,nullable=False),sa.Column("close",sa.Float,nullable=False),
        sa.Column("volume",sa.BigInteger,nullable=False),sa.Column("open_interest",sa.BigInteger,nullable=False),sa.Column("underlying_close",sa.Float,nullable=False),
        sa.Column("contract_source",sa.String(40),nullable=False),sa.Column("source_sha256",sa.String(64),nullable=False),sa.Column("source_filename",sa.String(255),nullable=False),
        sa.Column("ingestion_batch_id",sa.String(36),sa.ForeignKey("eod_ingestion_batches.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("created_at",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.UniqueConstraint("trade_date","instrument_id",name="uq_nifty_option_eod_trade_instrument"))
    op.create_index("ix_nifty_option_eod_expiry_strike","nifty_option_eod_bars",["expiry","strike"])
    op.create_index("ix_nifty_option_eod_batch","nifty_option_eod_bars",["ingestion_batch_id"])

def downgrade():
    op.drop_index("ix_nifty_option_eod_batch",table_name="nifty_option_eod_bars")
    op.drop_index("ix_nifty_option_eod_expiry_strike",table_name="nifty_option_eod_bars")
    op.drop_table("nifty_option_eod_bars")
    op.drop_table("nifty50_eod_bars")
    op.drop_index("ix_eod_ingestion_batches_status",table_name="eod_ingestion_batches")
    op.drop_index("ix_eod_ingestion_batches_trade_date",table_name="eod_ingestion_batches")
    op.drop_table("eod_ingestion_batches")
