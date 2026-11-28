"""Add post comments.

Revision ID: 4fb28f5dcb13
Revises: b67257fc1b08
"""

import sqlalchemy as sa
from alembic import op

revision = "4fb28f5dcb13"
down_revision = "b67257fc1b08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(body) BETWEEN 1 AND 1000", name="ck_comments_body_length"),
    )
    op.create_index("ix_comments_post_order", "comments", ["post_id", "created_at", "id"])
    op.create_index("ix_comments_author_id", "comments", ["author_id"])


def downgrade() -> None:
    op.drop_table("comments")
