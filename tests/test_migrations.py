from pathlib import Path

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError

from blogs_api.database import Base
from blogs_api.utils import verify_password


def config_for(connection):
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["connection"] = connection
    return config


def test_migrated_schema_matches_models(engine):
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        assert compare_metadata(context, Base.metadata) == []


def test_legacy_posts_are_preserved_and_backfilled():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            config = config_for(connection)
            command.upgrade(config, "3eecf97d0d4d")
            connection.execute(text(
                "INSERT INTO posts (id, title, content, published, rating) "
                "VALUES (1, 'Same title', NULL, false, 0), (2, 'Same title', 'Existing content', true, 4)"
            ))
            command.upgrade(config, "head")
            rows = connection.execute(text("SELECT id, slug, content, owner_id FROM posts ORDER BY id")).mappings().all()
            owner_id = rows[0]["owner_id"]
            assert owner_id is not None
            assert rows[0] == {"id": 1, "slug": "same-title-1", "content": "", "owner_id": owner_id}
            assert rows[1] == {"id": 2, "slug": "same-title-2", "content": "Existing content", "owner_id": owner_id}
            password = connection.execute(text("SELECT password FROM users WHERE id = :id"), {"id": owner_id}).scalar_one()
            assert not verify_password("!disabled", password)
            assert "votes" in inspect(connection).get_table_names()
    finally:
        engine.dispose()


def test_existing_votes_survive_foundation_upgrade():
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            config = config_for(connection)
            command.upgrade(config, "7b40c5d184a2")
            connection.execute(text("INSERT INTO users (id, username, email, password) VALUES (1, 'tester', 'test@example.com', 'unused')"))
            connection.execute(text("INSERT INTO posts (id, title, content, published, rating, owner_id) VALUES (1, 'Existing post', 'Content', true, 0, 1)"))
            Base.metadata.tables["votes"].create(connection)
            connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 1)"))
            command.upgrade(config, "head")
            assert connection.execute(text("SELECT user_id, post_id FROM votes")).all() == [(1, 1)]
            assert connection.execute(text("SELECT slug FROM posts")).scalar_one() == "existing-post-1"
    finally:
        engine.dispose()


def test_downgrade_and_reupgrade(engine):
    with engine.begin() as connection:
        config = config_for(connection)
        command.downgrade(config, "base")
        assert set(inspect(connection).get_table_names()) <= {"alembic_version"}
        command.upgrade(config, "head")
        assert {"users", "posts", "votes"} <= set(inspect(connection).get_table_names())


def test_author_migration_preserves_owners_and_votes_with_foreign_keys(engine):
    with engine.begin() as connection:
        config = config_for(connection)
        command.downgrade(config, "92f615a3e807")
        connection.execute(text("INSERT INTO users (id, username, email, password) VALUES (1, 'owner', 'owner@example.com', 'unused')"))
        connection.execute(text(
            "INSERT INTO posts (id, title, slug, content, published, rating, owner_id) VALUES "
            "(1, 'Owned', 'owned', 'Content', true, 0, 1), "
            "(2, 'Legacy', 'legacy', 'Content', false, 0, NULL)"
        ))
        connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 1), (1, 2)"))
        command.upgrade(config, "head")
        owners = connection.execute(text("SELECT owner_id FROM posts ORDER BY id")).scalars().all()
        assert owners[0] == 1
        assert owners[1] is not None and owners[1] != 1
        assert connection.execute(text("SELECT user_id, post_id FROM votes ORDER BY post_id")).all() == [(1, 1), (1, 2)]
        assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
        command.downgrade(config, "92f615a3e807")
        command.upgrade(config, "head")
        assert connection.execute(text("SELECT owner_id FROM posts ORDER BY id")).scalars().all() == owners
        assert connection.execute(text("SELECT user_id, post_id FROM votes ORDER BY post_id")).all() == [(1, 1), (1, 2)]
        assert connection.execute(text("SELECT COUNT(*) FROM users")).scalar_one() == 2


@pytest.mark.parametrize("backend", ["engine", "postgres_engine"])
def test_publication_migration_preserves_posts_and_votes(request, backend):
    with request.getfixturevalue(backend).begin() as connection:
        config = config_for(connection)
        if backend == "engine":
            command.downgrade(config, "a10b62d839ef")
        else:
            command.upgrade(config, "head")
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
            command.downgrade(config, "a10b62d839ef")
        connection.execute(text("INSERT INTO users (id, username, email, password) VALUES (1, 'author', 'author@example.com', 'unused')"))
        connection.execute(text(
            "INSERT INTO posts (id, title, slug, content, published, rating, owner_id) VALUES "
            "(1, 'Published', 'published', 'First', true, 4, 1), "
            "(2, 'Private', 'private', 'Second', false, 2, 1), "
            "(3, 'To archive', 'to-archive', 'Third', true, 3, 1)"
        ))
        connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 1), (1, 2), (1, 3)"))
        post_fields = "id, title, slug, content, rating, owner_id, created_at, updated_at"
        query = text(f"SELECT {post_fields} FROM posts ORDER BY id")
        original = connection.execute(query).all()
        command.upgrade(config, "head")
        assert connection.execute(query).all() == original
        rows = connection.execute(text("SELECT state, published_at, created_at FROM posts ORDER BY id")).all()
        assert [(row.state, row.published_at == row.created_at) for row in rows] == [
            ("published", True), ("draft", False), ("published", True),
        ]
        assert rows[1].published_at is None
        for assignment in ["state = 'other'", "state = 'published'", "owner_id = 999"]:
            with pytest.raises(IntegrityError), connection.begin_nested():
                connection.execute(text(f"UPDATE posts SET {assignment} WHERE id = 2"))
        connection.execute(text("UPDATE posts SET state = 'archived' WHERE id = 3"))
        command.downgrade(config, "a10b62d839ef")
        assert connection.execute(query).all() == original
        assert connection.execute(text("SELECT published FROM posts ORDER BY id")).scalars().all() == [True, False, False]
        assert connection.execute(text("SELECT user_id, post_id FROM votes ORDER BY post_id")).all() == [(1, 1), (1, 2), (1, 3)]
        with pytest.raises(IntegrityError), connection.begin_nested():
            connection.execute(text("INSERT INTO votes (user_id, post_id) VALUES (1, 999)"))
