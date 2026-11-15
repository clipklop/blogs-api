"""Add slugs, align nullability, and create votes."""
import re
import unicodedata

from alembic import op
import sqlalchemy as sa

revision = "92f615a3e807"
down_revision = "7b40c5d184a2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("slug", sa.String(160), nullable=True))
    connection = op.get_bind()
    posts = sa.table("posts", sa.column("id", sa.Integer()), sa.column("title", sa.String()), sa.column("slug", sa.String()), sa.column("content", sa.Text()))
    for post in connection.execute(sa.select(posts.c.id, posts.c.title)).mappings().all():
        title = unicodedata.normalize("NFKD", post["title"]).encode("ascii", "ignore").decode()
        prefix = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:120].rstrip("-") or "post"
        connection.execute(posts.update().where(posts.c.id == post["id"]).values(slug=f"{prefix}-{post['id']}"))
    connection.execute(posts.update().where(posts.c.content.is_(None)).values(content=""))
    with op.batch_alter_table("posts") as batch:
        batch.alter_column("content", existing_type=sa.Text(), nullable=False)
        batch.alter_column("owner_id", existing_type=sa.Integer(), nullable=True)
        batch.alter_column("slug", existing_type=sa.String(160), nullable=False)
        batch.create_index("ix_posts_slug", ["slug"], unique=True)
    # Some installations created votes manually before migrations were introduced.
    if not sa.inspect(connection).has_table("votes"):
        op.create_table(
            "votes",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("post_id", sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
        )


def downgrade():
    op.drop_table("votes")
    with op.batch_alter_table("posts") as batch:
        batch.drop_index("ix_posts_slug")
        batch.drop_column("slug")
        batch.alter_column("content", existing_type=sa.Text(), nullable=True)
