"""add owner id to posts

Revision ID: 7b40c5d184a2
Revises: 3eecf97d0d4d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b40c5d184a2"
down_revision: Union[str, Sequence[str], None] = "3eecf97d0d4d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing posts predate authentication, so their owner remains unknown.
    with op.batch_alter_table("posts") as batch:
        batch.add_column(sa.Column("owner_id", sa.Integer(), nullable=True))
        batch.create_foreign_key(
            "fk_posts_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade() -> None:
    with op.batch_alter_table("posts") as batch:
        batch.drop_constraint("fk_posts_owner_id_users", type_="foreignkey")
        batch.drop_column("owner_id")
