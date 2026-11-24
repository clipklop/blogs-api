"""Give legacy posts an author and require ownership."""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "a10b62d839ef"
down_revision = "92f615a3e807"
branch_labels = None
depends_on = None


def alter_owner_nullability(nullable):
    connection = op.get_bind()
    votes = None
    saved_votes = []
    if connection.dialect.name == "sqlite":
        # Batch recreation drops posts; detach votes first to prevent ON DELETE
        # CASCADE from silently deleting them when foreign keys are enabled.
        votes = sa.Table("votes", sa.MetaData(), autoload_with=connection)
        saved_votes = [dict(row) for row in connection.execute(sa.select(votes)).mappings()]
        votes.drop(connection)
    with op.batch_alter_table("posts") as batch:
        batch.alter_column("owner_id", existing_type=sa.Integer(), nullable=nullable)
    if votes is not None:
        votes.create(connection)
        if saved_votes:
            connection.execute(votes.insert(), saved_votes)


def upgrade():
    connection = op.get_bind()
    posts = sa.table("posts", sa.column("owner_id", sa.Integer()))
    if connection.execute(sa.select(sa.func.count()).select_from(posts).where(posts.c.owner_id.is_(None))).scalar_one():
        users = sa.table(
            "users", sa.column("id", sa.Integer()), sa.column("username", sa.String()),
            sa.column("email", sa.String()), sa.column("password", sa.String()),
        )
        suffix = uuid4().hex
        # This sentinel is not a password hash, so the legacy account cannot log in.
        owner_id = connection.execute(users.insert().values(
            username=f"legacy-{suffix}", email=f"legacy-{suffix}@example.com",
            password="!disabled",
        ).returning(users.c.id)).scalar_one()
        connection.execute(posts.update().where(posts.c.owner_id.is_(None)).values(owner_id=owner_id))
    alter_owner_nullability(False)


def downgrade():
    alter_owner_nullability(True)
