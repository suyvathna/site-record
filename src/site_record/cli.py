"""
Command line entry point.

    site-record ingest <export_dir> --project DEMO-001
    site-record days --project DEMO-001

`days` is the first thing to run on a real export: it shows per site-day how
many messages, photos, voice notes and files arrived, and who sent them.
That table alone tells you whether a group is rich enough to build records from.
"""

import argparse
from collections import defaultdict
from pathlib import Path

from .ingest.telegram_export import parse_export
from .models import MediaKind
from .normalize import site_date
from .store import EvidenceStore

DATA_ROOT = Path("data")


def _store(project: str) -> EvidenceStore:
    return EvidenceStore(DATA_ROOT / project)


def cmd_ingest(args) -> None:
    chat_id, chat_name, messages = parse_export(args.export_dir)
    store = _store(args.project)
    inserted, skipped = store.ingest(messages, args.export_dir)
    store.close()
    print(f"Chat: {chat_name} ({chat_id})")
    print(f"Parsed {len(messages)} messages: {inserted} new, {skipped} already stored")


def cmd_days(args) -> None:
    store = _store(args.project)
    rows = defaultdict(lambda: defaultdict(int))
    senders = defaultdict(set)
    for m in store.messages():
        day = site_date(m.sent_at_utc, args.tz)
        rows[day]["msgs"] += 1
        if m.text.strip():
            rows[day]["text"] += 1
        if m.attachment:
            rows[day][m.attachment.kind.value] += 1
        if m.sender_name:
            senders[day].add(m.sender_name)
    store.close()

    cols = ["msgs", "text", MediaKind.PHOTO.value, MediaKind.VOICE.value,
            MediaKind.EXCEL.value, MediaKind.PDF.value, MediaKind.VIDEO.value]
    print("date        " + "".join(f"{c:>8}" for c in cols) + "  senders")
    for day in sorted(rows):
        r = rows[day]
        print(f"{day}  " + "".join(f"{r[c]:>8}" for c in cols) + f"  {len(senders[day])}")


def main() -> None:
    p = argparse.ArgumentParser(prog="site-record")
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("ingest", help="Ingest a Telegram Desktop JSON export")
    pi.add_argument("export_dir")
    pi.add_argument("--project", required=True)
    pi.set_defaults(func=cmd_ingest)

    pd = sub.add_parser("days", help="Per-day activity summary of stored messages")
    pd.add_argument("--project", required=True)
    pd.add_argument("--tz", default="Asia/Phnom_Penh")
    pd.set_defaults(func=cmd_days)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
