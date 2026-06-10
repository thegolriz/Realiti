"""added parent_reply_id to replies

Revision ID: a1b2c3d4e5f6
Revises: 0228baf86e4e
Create Date: 2026-06-04 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "0228baf86e4e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "replies",
        sa.Column("parent_reply_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_replies_parent_reply_id",
        "replies",
        "replies",
        ["parent_reply_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_replies_parent_reply_id", "replies", type_="foreignkey")
    op.drop_column("replies", "parent_reply_id")
