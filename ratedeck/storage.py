from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
MIGRATION = """
CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS app_settings(key TEXT PRIMARY KEY, value_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL, updated_by_admin_id INTEGER);
CREATE TABLE IF NOT EXISTS assets(id INTEGER PRIMARY KEY, canonical_key TEXT UNIQUE NOT NULL, symbol TEXT NOT NULL, display_name TEXT NOT NULL, family TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, discovery_source TEXT NOT NULL, caption_emoji_json TEXT, favorite INTEGER NOT NULL DEFAULT 0, first_seen_at TEXT NOT NULL, last_seen_at TEXT NOT NULL, missing_since TEXT);
CREATE TABLE IF NOT EXISTS asset_aliases(id INTEGER PRIMARY KEY, asset_id INTEGER NOT NULL REFERENCES assets(id), raw_alias TEXT NOT NULL, normalized_alias TEXT NOT NULL, source TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, UNIQUE(asset_id, normalized_alias, source));
CREATE INDEX IF NOT EXISTS ix_alias_normalized ON asset_aliases(normalized_alias);
CREATE TABLE IF NOT EXISTS asset_source_mappings(asset_id INTEGER NOT NULL REFERENCES assets(id), provider_id TEXT NOT NULL, provider_asset_id TEXT NOT NULL, status TEXT NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(asset_id, provider_id));
CREATE TABLE IF NOT EXISTS markets(id INTEGER PRIMARY KEY, provider_id TEXT NOT NULL, provider_market_key TEXT NOT NULL, base_key TEXT NOT NULL, quote_key TEXT NOT NULL, usable INTEGER NOT NULL, last_seen_at TEXT NOT NULL, metadata_json TEXT NOT NULL DEFAULT '{}', UNIQUE(provider_id, provider_market_key));
CREATE TABLE IF NOT EXISTS provider_state(provider_key TEXT PRIMARY KEY, enabled INTEGER NOT NULL DEFAULT 1, last_attempt TEXT, last_success TEXT, last_failure TEXT, last_error TEXT, latency_ms INTEGER, cooldown_until TEXT, consecutive_failures INTEGER NOT NULL DEFAULT 0, request_count INTEGER NOT NULL DEFAULT 0, snapshot_json TEXT, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS provider_secrets(provider_key TEXT PRIMARY KEY, ciphertext BLOB NOT NULL, key_fingerprint TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS rates_current(source_key TEXT NOT NULL, target_key TEXT NOT NULL, provider_id TEXT NOT NULL, rate_decimal TEXT NOT NULL, source_updated_at TEXT NOT NULL, provenance_json TEXT NOT NULL, PRIMARY KEY(source_key,target_key,provider_id));
CREATE TABLE IF NOT EXISTS market_history(id INTEGER PRIMARY KEY, source_key TEXT NOT NULL, target_key TEXT NOT NULL, provider_id TEXT NOT NULL, timestamp TEXT NOT NULL, value_decimal TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS ix_history_pair_time ON market_history(source_key,target_key,timestamp);
CREATE TABLE IF NOT EXISTS stars_packages(quantity TEXT PRIMARY KEY, price_toman TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL, updated_by_admin_id INTEGER);
CREATE TABLE IF NOT EXISTS text_templates(key TEXT PRIMARY KEY, scope TEXT NOT NULL, rich_document_json TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1, enabled INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL, updated_by_admin_id INTEGER);
CREATE TABLE IF NOT EXISTS button_customizations(button_key TEXT PRIMARY KEY, label TEXT, style TEXT, icon_custom_emoji_id TEXT, enabled INTEGER, row_override INTEGER, order_override INTEGER, revision INTEGER NOT NULL DEFAULT 1, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_events(id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, actor TEXT NOT NULL, action TEXT NOT NULL, object_type TEXT NOT NULL, object_key TEXT NOT NULL, result TEXT NOT NULL, metadata_json TEXT NOT NULL, correlation_id TEXT);
"""

def now() -> str: return datetime.now(UTC).isoformat()

class Database:
    def __init__(self, path: str | Path = ":memory:"):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys=ON")

    def migrate(self) -> None:
        with self.connection:
            self.connection.executescript(MIGRATION)
            self.connection.execute("INSERT OR IGNORE INTO schema_migrations VALUES (?,?)", (SCHEMA_VERSION, now()))

    def audit(self, actor: str, action: str, kind: str, key: str, result: str = "ok", metadata: dict[str, Any] | None = None) -> None:
        safe = {k: v for k, v in (metadata or {}).items() if not any(s in k.lower() for s in ("token", "secret", "key", "password"))}
        with self.connection:
            self.connection.execute("INSERT INTO audit_events(timestamp,actor,action,object_type,object_key,result,metadata_json) VALUES(?,?,?,?,?,?,?)", (now(), actor, action, kind, key, result, json.dumps(safe, ensure_ascii=False)))

