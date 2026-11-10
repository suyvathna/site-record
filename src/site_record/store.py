"""
Evidence store: raw messages and files exactly as received.

This layer is never edited. SQLite triggers reject UPDATE and DELETE on
raw_messages, so even a bug in later code can't rewrite history. Re-ingesting
the same export is safe: existing (chat_id, message_id) rows are skipped.

Files are copied into data/<project>/media/ under their SHA-256 hash. The
hash is stored with the message, so anyone can later prove a photo in a claim
pack is byte-identical to what arrived in the group that day.
"""

import hashlib
import json
import shutil
import sqlite3
from pathlib import Path

from .models import Message

_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_messages (
    chat_id         TEXT    NOT NULL,
    message_id      INTEGER NOT NULL,
    sent_at_utc     TEXT    NOT NULL,
    sender_id       TEXT,
    sender_name     TEXT,
    text            TEXT    NOT NULL DEFAULT '',
    media_kind      TEXT,
    media_path      TEXT,          -- path inside the store, not the export
    media_sha256    TEXT,
    message_json    TEXT    NOT NULL,  -- full normalised Message for audit
    ingested_at_utc TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (chat_id, message_id)
);

CREATE TRIGGER IF NOT EXISTS raw_messages_no_update
BEFORE UPDATE ON raw_messages
BEGIN SELECT RAISE(ABORT, 'raw_messages is append-only'); END;

CREATE TRIGGER IF NOT EXISTS raw_messages_no_delete
BEFORE DELETE ON raw_messages
BEGIN SELECT RAISE(ABORT, 'raw_messages is append-only'); END;
"""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class EvidenceStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.media_dir = self.root / "media"
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.root / "evidence.sqlite")
        self.conn.executescript(_SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def ingest(self, messages: list[Message], export_dir: str | Path) -> tuple[int, int]:
        """Returns (inserted, skipped_existing)."""
        export_dir = Path(export_dir)
        inserted = skipped = 0

        for msg in messages:
            stored_path = None
            att = msg.attachment
            if att and att.path:
                src = export_dir / att.path
                if src.exists():
                    att.sha256 = _sha256(src)
                    dest = self.media_dir / f"{att.sha256}{src.suffix.lower()}"
                    if not dest.exists():
                        shutil.copy2(src, dest)
                    stored_path = str(dest.relative_to(self.root))

            cur = self.conn.execute(
                """INSERT OR IGNORE INTO raw_messages
                   (chat_id, message_id, sent_at_utc, sender_id, sender_name, text,
                    media_kind, media_path, media_sha256, message_json)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    msg.chat_id,
                    msg.message_id,
                    msg.sent_at_utc.isoformat(),
                    msg.sender_id,
                    msg.sender_name,
                    msg.text,
                    att.kind.value if att else None,
                    stored_path,
                    att.sha256 if att else None,
                    msg.model_dump_json(),
                ),
            )
            if cur.rowcount:
                inserted += 1
            else:
                skipped += 1

        self.conn.commit()
        return inserted, skipped

    def messages(self, chat_id: str | None = None) -> list[Message]:
        sql = "SELECT message_json FROM raw_messages"
        args: tuple = ()
        if chat_id:
            sql += " WHERE chat_id = ?"
            args = (chat_id,)
        sql += " ORDER BY sent_at_utc, message_id"
        return [Message.model_validate(json.loads(r[0])) for r in self.conn.execute(sql, args)]
