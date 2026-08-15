from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    admin_ids: frozenset[int]
    database_path: Path = Path("ratedeck.db")
    master_key_path: Path = Path("ratedeck.key")
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("RATEDECK_BOT_TOKEN", "").strip()
        admins = frozenset(int(v.strip()) for v in os.getenv("RATEDECK_ADMIN_IDS", "").split(",") if v.strip())
        return cls(token, admins, Path(os.getenv("RATEDECK_DATABASE", "ratedeck.db")),
                   Path(os.getenv("RATEDECK_MASTER_KEY", "ratedeck.key")), os.getenv("RATEDECK_LOG_LEVEL", "INFO"))

