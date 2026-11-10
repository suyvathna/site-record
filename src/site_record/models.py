"""
The common message object every ingest source produces.

Phase 1 reads a Telegram Desktop export, Phase 2 reads live webhook updates.
Both must produce `Message`, so nothing downstream of ingest knows or cares
where a message came from. That is what lets Phase 1 code carry into Phase 2
unchanged.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MediaKind(str, Enum):
    PHOTO = "photo"
    VOICE = "voice"          # stored, never transcribed in v1 (decision 0002)
    VIDEO = "video"
    EXCEL = "excel"          # content extracted in v1
    PDF = "pdf"              # stored and listed only in v1
    WORD = "word"            # stored and listed only in v1
    OTHER_FILE = "other_file"
    STICKER = "sticker"


class Attachment(BaseModel):
    kind: MediaKind
    path: str | None = None          # relative to the export folder; None if not exported
    mime_type: str | None = None
    file_name: str | None = None
    sha256: str | None = None        # filled by the store when the file exists
    duration_seconds: int | None = None


class Message(BaseModel):
    chat_id: str
    message_id: int
    sent_at_utc: datetime            # always timezone-aware UTC
    sender_id: str | None = None
    sender_name: str | None = None
    text: str = ""                   # message text or media caption, plain string
    reply_to_message_id: int | None = None
    forwarded_from: str | None = None
    edited_at_utc: datetime | None = None
    attachment: Attachment | None = None
