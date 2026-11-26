from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from queue import Queue
from time import monotonic, sleep

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from blogs_api import models
from blogs_api.routers.post import set_publication
from blogs_api.routers.vote import vote
from blogs_api.schemas import PostPublication, VotePost
from conftest import migrate


@pytest.mark.parametrize("competing_vote", [False, True], ids=["archive-publish", "unpublish-vote"])
def test_waiting_request_evaluates_committed_post_state(postgres_engine, competing_vote):
    with postgres_engine.begin() as connection:
        migrate(connection)
    with Session(postgres_engine) as db:
        db.add(models.User(id=1, username="owner", email="owner@example.com", password="unused"))
        db.flush()
        db.add(models.Post(
            id=1, owner_id=1, title="Post", slug="post", content="Text",
            state="published" if competing_vote else "draft",
            published_at=datetime.now(timezone.utc) if competing_vote else None,
        ))
        db.commit()

    waiting_pid = Queue()

    def competing_request():
        with Session(postgres_engine) as db:
            db.execute(text("SET LOCAL lock_timeout = '10s'"))
            waiting_pid.put(db.scalar(text("SELECT pg_backend_pid()")))
            user = db.get(models.User, 1)
            if competing_vote:
                return vote(VotePost(post_id=1, user_id=1, dir=1), user, db)
            return set_publication(1, PostPublication(state="published"), db, user)

    target = "draft" if competing_vote else "archived"
    with ThreadPoolExecutor(max_workers=1) as pool, postgres_engine.connect() as connection:
        with connection.begin():
            with Session(bind=connection, join_transaction_mode="create_savepoint") as db:
                set_publication(1, PostPublication(state=target), db, db.get(models.User, 1))
            blocker_pid = connection.scalar(text("SELECT pg_backend_pid()"))
            future = pool.submit(competing_request)
            pid = waiting_pid.get(timeout=5)
            deadline = monotonic() + 5
            while monotonic() < deadline:
                blockers = connection.scalar(text("SELECT pg_blocking_pids(:pid)"), {"pid": pid})
                if blocker_pid in blockers:
                    break
                sleep(0.02)
            else:
                pytest.fail("Expected the competing operation to wait on the post lock")
        with pytest.raises(HTTPException) as error:
            future.result(timeout=10)
        assert error.value.status_code == (404 if competing_vote else 409)
        with Session(postgres_engine) as db:
            assert db.get(models.Post, 1).state == target
            assert db.get(models.Vote, (1, 1)) is None
