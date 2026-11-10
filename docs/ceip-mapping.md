# Mapping to CEIP

Source: `suyvathna/CEIP` at commit 1230a6e, `backend/app/schemas/daily_log.py` and `backend/app/constants/`.

## Same in both

`schema.DailyRecord` uses CEIP's `DailyLogCreate` field names for the Notes block (`work_completed`, `delays`, `engineer_instruction`, `tomorrow_plan`, `remarks`), the narrative fields (`manpower_notes`, `equipment_notes`, `materials_notes`, `hse_notes`, `visitor_notes`) and the structured lists (`weather_observations`, `manpower_entries`, `equipment_entries`, `delivery_entries`, `inspection_entries`, `hse_entries`, `visitor_entries`). Entry fields match CEIP's `*EntryCreate` models. `tests/test_schema.py` fails if a CEIP field name goes missing here.

`EventType` and `PhotoCategory` are copied into `ceip_enums.py`.

## Only in site-record

| Field | Why | Where it goes in CEIP later |
|---|---|---|
| `source_message_ids` on every entry | Traceability to the evidence store | New column, or Evidence link |
| `confirmed` on every entry | Engineer approval | New column |
| `photos` (PhotoRef) | Photos with hash and category | Evidence rows (CEIP stores files in MinIO) |
| `documents` | Voice, PDF, Word listed but unread | Evidence rows, kind GENERAL_EVIDENCE |
| `event_candidates` | Possible delay/claim events | Events, only after confirmation |
| `gaps` | Questions for the evening check | Not stored in CEIP |
| `project_code` | CEIP uses `project_id` UUID | Look up the UUID at push time |

## Only in CEIP (not filled by site-record v1)

`temp_avg_c`, `humidity_avg_pct` (official weather data, not from chat), `event_id`, `additional_event_ids`.
