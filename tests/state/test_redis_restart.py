"""Opt-in integration test against a dedicated Redis database and real RQ workers."""

import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from redis import Redis
from sqlalchemy import select

from backend.core.schemas.models import Scope
from backend.core.workflow import Mutation, State, Workflow
from backend.storage.database import migrate_state, state_engine
from backend.storage.state_schema import events, jobs, runs
from backend.workers.state_queue import REDELIVERY_SECONDS, dispatch_pending, state_queue

ROOT = Path(__file__).resolve().parents[2]
CRASH_BEFORE_COMMIT = """
import os

from redis import Redis
from rq import SimpleWorker
from rq.serializers import JSONSerializer

from backend.core import workflow
from backend.workers.state_queue import state_queue

apply_transition = workflow._apply_transition


def interrupt_after_write(*args, **kwargs):
    apply_transition(*args, **kwargs)
    os._exit(19)


workflow._apply_transition = interrupt_after_write
with Redis.from_url(os.environ['GENESIS_REDIS_URL']) as redis:
    SimpleWorker([state_queue(redis)], connection=redis, serializer=JSONSerializer).work(burst=True)
"""


def test_killed_rq_worker_rolls_back_and_restart_applies_exactly_once(tmp_path):
    redis_url = os.environ["GENESIS_STATE_TEST_REDIS_URL"]
    database = tmp_path / "restart.db"
    env = dict(os.environ, GENESIS_DATABASE_PATH=str(database), GENESIS_REDIS_URL=redis_url)
    engine = state_engine(database)
    try:
        migrate_state(engine)
        workflow = Workflow(engine)
        scope = Scope(
            project_id="project:restart",
            version_id="version:original",
            analysis_id="analysis:restart",
            run_id="run:restart",
            source_revision="a" * 40,
            baseline_sha256="b" * 64,
        )
        actor = "actor:restart"
        workflow.register_version(
            scope.project_id,
            scope.version_id,
            scope.version_id,
            scope.baseline_sha256,
            Mutation(actor, "register"),
        )
        workflow.create_run(scope, Mutation(actor, "create"))
        job_id = workflow.enqueue_transition(
            scope.run_id, State.UPLOADED, State.BASELINE_CREATED, Mutation(actor, "queue")
        )
        now = datetime.now(UTC)
        with Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2) as redis:
            assert redis.ping() and redis.dbsize() == 0, "Use a dedicated empty Redis database."
            queue = state_queue(redis)
            assert dispatch_pending(engine, queue, now=now) == 1
            interrupted = subprocess.run(
                [sys.executable, "-B", "-c", CRASH_BEFORE_COMMIT],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            assert interrupted.returncode == 19, interrupted.stdout + interrupted.stderr
            with engine.connect() as connection:
                assert connection.scalar(select(runs.c.state)) == State.UPLOADED
                assert connection.scalar(select(jobs.c.status)) == "QUEUED"
                assert (
                    connection.scalar(select(events.c.id).where(events.c.job_id == job_id)) is None
                )
            retry = timedelta(seconds=REDELIVERY_SECONDS)
            assert dispatch_pending(engine, queue, now=now + retry) == 1
            assert dispatch_pending(engine, queue, now=now + 2 * retry) == 1

        restarted = subprocess.run(
            [sys.executable, "-B", "-m", "backend.workers.state_queue", "worker", "--burst"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert restarted.returncode == 0, restarted.stdout + restarted.stderr
        with engine.connect() as connection:
            assert connection.scalar(select(runs.c.state)) == State.BASELINE_CREATED
            assert connection.scalar(select(jobs.c.status)) == "COMPLETED"
            assert (
                len(connection.execute(select(events).where(events.c.job_id == job_id)).all()) == 1
            )
    finally:
        engine.dispose()
