"""add post review_status and review_reason

Revision ID: d1e2f3a4b5c6
Revises: c855c01a645e
Create Date: 2026-07-23 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d1e2f3a4b5c6"
down_revision = "c855c01a645e"
branch_labels = None
depends_on = None


def upgrade():
    # server_default "clean" backfills existing posts so they stay public.
    op.add_column(
        "post",
        sa.Column(
            "review_status",
            sa.String(),
            server_default="clean",
            nullable=True,
        ),
    )
    op.add_column("post", sa.Column("review_reason", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("post", "review_reason")
    op.drop_column("post", "review_status")
