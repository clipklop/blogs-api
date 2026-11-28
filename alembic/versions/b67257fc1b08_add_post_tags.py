"""Add post tags

Revision ID: b67257fc1b08
Revises: 61d07bfb923e
"""

import sqlalchemy as sa
from alembic import op


revision = "b67257fc1b08"
down_revision = "61d07bfb923e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tags", sa.Column("name", sa.String(32), primary_key=True))
    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_name", sa.String(32), sa.ForeignKey("tags.name", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_post_tags_tag_name", "post_tags", ["tag_name"])


def downgrade() -> None:
    op.drop_table("post_tags")
    op.drop_table("tags")
