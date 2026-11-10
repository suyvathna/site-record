from datetime import date

from site_record.ceip_enums import EventType
from site_record.schema import DailyRecord, MessageExtraction


def test_extraction_discriminated_union():
    raw = {
        "message_id": 3,
        "language": "km",
        "is_site_relevant": True,
        "items": [
            {"section": "manpower", "trade": "general labour", "workers_count": 12,
             "evidence_quote": "កម្មករ 12 នាក់"},
            {"section": "manpower", "trade": "steel fixer", "workers_count": 6,
             "evidence_quote": "ជាងដែក 6 នាក់"},
            {"section": "event", "event_type": "Adverse Weather",
             "description": "Heavy rain 14:00-15:30, work stopped"},
        ],
    }
    ex = MessageExtraction.model_validate(raw)
    assert ex.items[0].workers_count == 12
    assert ex.items[2].event_type == EventType.ADVERSE_WEATHER


def test_daily_record_ceip_fields_present():
    # Field names CEIP's DailyLogCreate expects. If CEIP renames one, this fails.
    ceip_fields = {
        "diary_date", "work_completed", "delays", "engineer_instruction",
        "tomorrow_plan", "remarks", "manpower_notes", "equipment_notes",
        "materials_notes", "hse_notes", "visitor_notes", "weather_observations",
        "manpower_entries", "equipment_entries", "delivery_entries",
        "inspection_entries", "hse_entries", "visitor_entries",
    }
    assert ceip_fields <= set(DailyRecord.model_fields)
    DailyRecord(project_code="DEMO-001", diary_date=date(2026, 11, 2))
