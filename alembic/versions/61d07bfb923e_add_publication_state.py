"""Replace the publication flag with a state and first publication time."""

from contextlib import contextmanager

import sqlalchemy as sa
from alembic import op

revision = "61d07bfb923e"
down_revision = "a10b62d839ef"
branch_labels = None
depends_on = None


@contextmanager
def preserve_votes():
    connection = op.get_bind()
    if connection.dialect.name != "sqlite":
        yield
        return

    # SQLite batch mode rebuilds posts. Temporarily detach votes to avoid cascades.
    votes = sa.Table("votes", sa.MetaData(), autoload_with=connection)
    saved_votes = [dict(row) for row in connection.execute(sa.select(votes)).mappings()]
    votes.drop(connection)
    yield
    votes.create(connection)
    if saved_votes:
        connection.execute(votes.insert(), saved_votes)


def upgrade():
    op.add_column("posts", sa.Column("state", sa.String(9), nullable=False, server_default="draft"))
    op.add_column("posts", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE posts SET state = 'published', published_at = created_at WHERE published IS TRUE")

    with preserve_votes(), op.batch_alter_table("posts") as batch:
        batch.create_check_constraint("ck_posts_state", "state IN ('draft', 'published', 'archived')")
        batch.create_check_constraint("ck_posts_publication_time", "state <> 'published' OR published_at IS NOT NULL")
        batch.drop_column("published")


def downgrade():
    op.add_column("posts", sa.Column("published", sa.Boolean(), nullable=True))
    op.execute("UPDATE posts SET published = (state = 'published')")

    with preserve_votes(), op.batch_alter_table("posts") as batch:
        batch.drop_constraint("ck_posts_publication_time", type_="check")
        batch.drop_constraint("ck_posts_state", type_="check")
        batch.alter_column("published", existing_type=sa.Boolean(), nullable=False)
        batch.drop_column("published_at")
        batch.drop_column("state")
