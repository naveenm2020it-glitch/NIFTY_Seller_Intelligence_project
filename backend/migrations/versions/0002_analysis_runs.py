"""Phase 2 persistent configuration and orchestration lifecycle."""
from alembic import op
import sqlalchemy as sa
revision = "0002_analysis_runs"
down_revision = "0001_initial_baseline"
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.create_table("analysis_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("analysis_date", sa.Date(), nullable=False),
        sa.Column("selected_expiry", sa.Date(), nullable=False),
        sa.Column("expiry_selection_mode", sa.String(10), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("config_snapshot", sa.JSON(), nullable=False),
        sa.Column("source_provenance", sa.JSON(), nullable=False),
        sa.Column("stage_results", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_analysis_runs_idempotency_key"))
    op.create_index("ix_analysis_runs_idempotency_key", "analysis_runs", ["idempotency_key"])
    op.create_index("ix_analysis_runs_analysis_date", "analysis_runs", ["analysis_date"])
    op.create_index("ix_analysis_runs_status", "analysis_runs", ["status"])
def downgrade() -> None:
    op.drop_index("ix_analysis_runs_status", table_name="analysis_runs")
    op.drop_index("ix_analysis_runs_analysis_date", table_name="analysis_runs")
    op.drop_index("ix_analysis_runs_idempotency_key", table_name="analysis_runs")
    op.drop_table("analysis_runs")
