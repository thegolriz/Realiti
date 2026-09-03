"""seed initial tags

Revision ID: eb74f756ce8b
Revises: de921c4b8da6
Create Date: 2026-09-03 04:15:04.818051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb74f756ce8b'
down_revision = 'de921c4b8da6'
branch_labels = None
depends_on = None

tag_table = sa.table("tag", sa.column("tagName", sa.String))


def upgrade():
    op.bulk_insert(tag_table, [
        {"tagName": "review"},
        {"tagName": "question"},
        {"tagName": "discussion"},
        {"tagName": "recommendation"},
        {"tagName": "warning"}
    ])


def downgrade():
    op.execute(
        tag_table.delete().where(
            tag_table.c.tagName.in_(
                ["review", "question", "discussion", "recommendation", "warning"]
            )
        )
    )
