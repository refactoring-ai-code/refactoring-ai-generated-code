"""Environment-backed settings for the development services."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[1] / ".data" / "genesis.db"


@dataclass(frozen=True, slots=True)
class Settings:
    """Minimal settings needed by the F01-ENV health surface."""

    database_path: Path
    redis_url: str

    @classmethod
    def from_environment(cls) -> Settings:
        return cls(
            database_path=Path(os.getenv("GENESIS_DATABASE_PATH", str(DEFAULT_DATABASE_PATH))),
            redis_url=os.getenv("GENESIS_REDIS_URL", "redis://127.0.0.1:6379/0"),
        )
