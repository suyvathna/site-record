"""
Parse a Telegram Desktop chat export (Settings > Export chat history, format: JSON).

Expected layout of the export folder:
    result.json
    photos/...
    files/...
    voice_messages/...
    video_files/...

Format notes (from known export structure, NOT verified against a real site
group yet; check these on the first real export and record findings in
docs/decisions/):
- `date` is in the exporting computer's local time. Use `date_unixtime`
  (UTC epoch seconds) instead, always.
- `text` is either a plain string or a list mixing strings and entity dicts
  like {"type": "bold", "text": "..."}. Photo captions live in `text` too.
- When media was not downloaded, the path field holds a placeholder like
  "(File not included. Change data exporting settings to download.)".
- An album of N photos arrives as N messages; usually only the first has text.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from ..models import Attachment, MediaKind, Message

_NOT_INCLUDED_PREFIX = "(File not included"

_EXCEL_MIME = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
}
_WORD_MIME = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}


def _flatten_text(raw) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw
    parts = []
    for piece in raw:
        parts.append(piece if isinstance(piece, str) else piece.get("text", ""))
    return "".join(parts)


def _utc(epoch: str | int | None) -> datetime | None:
    if epoch is None:
        return None
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc)


def _clean_path(value: str | None) -> str | None:
    if not value or value.startswith(_NOT_INCLUDED_PREFIX):
        return None
    return value


def _attachment(m: dict) -> Attachment | None:
    if "photo" in m:
        return Attachment(kind=MediaKind.PHOTO, path=_clean_path(m["photo"]), mime_type="image/jpeg")

    if "file" not in m:
        return None

    media_type = m.get("media_type")
    mime = m.get("mime_type")
    path = _clean_path(m.get("file"))
    file_name = m.get("file_name") or (Path(path).name if path else None)
    duration = m.get("duration_seconds")

    if media_type == "voice_message":
        kind = MediaKind.VOICE
    elif media_type in ("video_file", "video_message", "animation"):
        kind = MediaKind.VIDEO
    elif media_type == "sticker":
        kind = MediaKind.STICKER
    elif mime in _EXCEL_MIME or (file_name or "").lower().endswith((".xlsx", ".xls")):
        kind = MediaKind.EXCEL
    elif mime == "application/pdf" or (file_name or "").lower().endswith(".pdf"):
        kind = MediaKind.PDF
    elif mime in _WORD_MIME or (file_name or "").lower().endswith((".docx", ".doc")):
        kind = MediaKind.WORD
    elif (mime or "").startswith("image/"):
        # Photos sent "as file" (uncompressed) are still photos.
        kind = MediaKind.PHOTO
    else:
        kind = MediaKind.OTHER_FILE

    return Attachment(kind=kind, path=path, mime_type=mime, file_name=file_name, duration_seconds=duration)


def parse_export(export_dir: str | Path) -> tuple[str, str, list[Message]]:
    """
    Returns (chat_id, chat_name, messages). Service messages
    (joins, pins, title changes) are skipped.
    """
    export_dir = Path(export_dir)
    data = json.loads((export_dir / "result.json").read_text(encoding="utf-8"))

    chat_id = str(data.get("id", "unknown"))
    chat_name = data.get("name", "")
    messages: list[Message] = []

    for m in data.get("messages", []):
        if m.get("type") != "message":
            continue
        messages.append(
            Message(
                chat_id=chat_id,
                message_id=int(m["id"]),
                sent_at_utc=_utc(m.get("date_unixtime")),
                sender_id=m.get("from_id"),
                sender_name=m.get("from"),
                text=_flatten_text(m.get("text")),
                reply_to_message_id=m.get("reply_to_message_id"),
                forwarded_from=m.get("forwarded_from"),
                edited_at_utc=_utc(m.get("edited_unixtime")),
                attachment=_attachment(m),
            )
        )
    return chat_id, chat_name, messages
