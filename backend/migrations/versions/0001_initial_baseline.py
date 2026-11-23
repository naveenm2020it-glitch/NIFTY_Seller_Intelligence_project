"""Initial migration baseline.

No domain tables are created until the approved analysis data model is finalized.
"""

from alembic import op

revision = "0001_initial_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
