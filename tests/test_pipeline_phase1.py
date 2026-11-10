"""
Tests for the parts of Phase 1 that exist: ingest, normalise, evidence store.
The fixture is synthetic (tests/fixtures/sample_export), written to cover the
cases a real Cambodian site group will throw at us.
"""

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from site_record.ingest.telegram_export import parse_export
from site_record.models import MediaKind
from site_record.normalize import khmer_digits_to_ascii, normalize_text, site_date
from site_record.store import EvidenceStore

FIXTURE = Path(__file__).parent / "fixtures" / "sample_export"


@pytest.fixture
def parsed():
    return parse_export(FIXTURE)


def test_service_messages_skipped(parsed):
    _, _, msgs = parsed
    assert [m.message_id for m in msgs] == list(range(2, 12))


def test_entity_text_flattened(parsed):
    msg4 = next(m for m in parsed[2] if m.message_id == 4)
    assert msg4.text == "ចាក់ slab ជាន់ទី ៣ grid A-C"


def test_attachment_kinds(parsed):
    kinds = {m.message_id: m.attachment.kind for m in parsed[2] if m.attachment}
    assert kinds[4] == MediaKind.PHOTO
    assert kinds[6] == MediaKind.VOICE
    assert kinds[8] == MediaKind.EXCEL
    assert kinds[9] == MediaKind.PHOTO


def test_missing_media_has_no_path(parsed):
    msg9 = next(m for m in parsed[2] if m.message_id == 9)
    assert msg9.attachment.path is None


def test_khmer_digits():
    assert khmer_digits_to_ascii("កម្មករ ១២ នាក់") == "កម្មករ 12 នាក់"
    assert normalize_text("  ជាន់ទី ៣ ") == "ជាន់ទី 3"


def test_site_date_uses_phnom_penh_not_utc(parsed):
    by_id = {m.message_id: m for m in parsed[2]}
    # 16:30 UTC = 23:30 in Phnom Penh, same day
    assert site_date(by_id[10].sent_at_utc) == date(2026, 11, 2)
    # 17:30 UTC on 2 Nov = 00:30 on 3 Nov in Phnom Penh
    assert by_id[11].sent_at_utc.date() == date(2026, 11, 2)
    assert site_date(by_id[11].sent_at_utc) == date(2026, 11, 3)


def test_store_is_idempotent_and_hashes_files(tmp_path, parsed):
    _, _, msgs = parsed
    store = EvidenceStore(tmp_path)
    assert store.ingest(msgs, FIXTURE) == (10, 0)
    assert store.ingest(msgs, FIXTURE) == (0, 10)
    stored = {m.message_id: m for m in store.messages()}
    assert len(stored[4].attachment.sha256) == 64
    assert stored[4].attachment.sha256 != stored[5].attachment.sha256
    store.close()


def test_store_is_append_only(tmp_path, parsed):
    store = EvidenceStore(tmp_path)
    store.ingest(parsed[2], FIXTURE)
    with pytest.raises(sqlite3.IntegrityError):
        store.conn.execute("UPDATE raw_messages SET text = 'tampered' WHERE message_id = 7")
    with pytest.raises(sqlite3.IntegrityError):
        store.conn.execute("DELETE FROM raw_messages WHERE message_id = 7")
    store.close()
