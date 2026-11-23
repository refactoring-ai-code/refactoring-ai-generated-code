"""Durable delivery of SQLite workflow jobs through the trusted Redis/RQ queue."""

import argparse
import logging
import os
from datetime import UTC, datetime, timedelta
from time import sleep

from backend.app.config import Settings
from backend.core.workflow import Workflow
from backend.storage.database import migrate_state, state_engine, state_write
from backend.storage.state_schema import jobs
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue, SimpleWorker, Worker
from rq.serializers import JSONSerializer
from sqlalchemy import Engine, select

QUEUE_NAME = "genesis-state"
REDELIVERY_SECONDS = 30


def state_queue(connection: Redis) -> Queue:
    return Queue(QUEUE_NAME, connection=connection, serializer=JSONSerializer)


def execute_job(job_id: str) -> bool:
    """RQ entry point. Each worker opens its configured shared database itself."""
    engine = state_engine(Settings.from_environment().database_path)
    try:
        return Workflow(engine).complete_job(job_id)
    finally:
        engine.dispose()


def dispatch_pending(engine: Engine, queue: Queue, *, now: datetime | None = None) -> int:
    """Publish a bounded batch, leaving failed or lost deliveries eligible for retry."""
    now = now or datetime.now(UTC)
    if now.utcoffset() != timedelta(0):
        raise ValueError("Dispatch time must be UTC.")
    cutoff = now.isoformat(timespec="microseconds").replace("+00:00", "Z")
    later = now + timedelta(seconds=REDELIVERY_SECONDS)
    retry_at = later.isoformat(timespec="microseconds").replace("+00:00", "Z")
    delivered = 0
    for _ in range(32):
        with state_write(engine) as connection:
            job_id = connection.scalar(
                select(jobs.c.id)
                .where(
                    jobs.c.status == "QUEUED",
                    jobs.c.dispatch_after <= cutoff,
                )
                .order_by(jobs.c.dispatch_after, jobs.c.id)
                .limit(1)
            )
            if job_id is None:
                break
            connection.execute(
                jobs.update().where(jobs.c.id == job_id).values(dispatch_after=retry_at)
            )
        # The reservation expires even if Redis accepts the message but the process dies.
        queue.enqueue_call(
            "backend.workers.state_queue.execute_job",
            args=(job_id,),
            timeout=10,
            ttl=REDELIVERY_SECONDS,
            result_ttl=0,
            failure_ttl=60,
            description="Apply workflow transition",
        )
        delivered += 1
    return delivered


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage durable Genesis workflow state jobs.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate")
    commands.add_parser("dispatch").add_argument("--watch", action="store_true")
    commands.add_parser("worker").add_argument("--burst", action="store_true")
    args = parser.parse_args()
    settings = Settings.from_environment()
    if args.command == "worker":
        with Redis.from_url(settings.redis_url, socket_connect_timeout=2) as redis:
            worker_class = SimpleWorker if os.name == "nt" else Worker
            worker_class(
                [state_queue(redis)],
                connection=redis,
                serializer=JSONSerializer,
                log_job_description=False,
            ).work(burst=args.burst)
        return
    engine = state_engine(settings.database_path)
    try:
        if args.command == "migrate":
            settings.database_path.parent.mkdir(parents=True, exist_ok=True)
            migrate_state(engine)
            return
        with Redis.from_url(
            settings.redis_url, socket_connect_timeout=2, socket_timeout=2
        ) as redis:
            queue = state_queue(redis)
            while True:
                try:
                    dispatch_pending(engine, queue)
                except RedisError:
                    if not args.watch:
                        raise SystemExit("Redis delivery unavailable. SQLite jobs remain pending.")
                    logging.warning("Redis delivery unavailable. SQLite jobs remain pending.")
                if not args.watch:
                    return
                sleep(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
