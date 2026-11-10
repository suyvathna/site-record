# 0001 Separate repo, CEIP-shaped output

Date: 2026-11-10. Status: accepted.

CEIP already has the Daily Log, Evidence, event and claim models but stalled on manual data entry. Building the Telegram capture inside CEIP would mean carrying its full stack (FastAPI, Postgres, MinIO, React) from day one.

Decision: a separate, lightweight repo whose output schema copies CEIP's `DailyLogCreate` and enums. It runs on SQLite and a folder of files. Later it can push records to CEIP's API.

Cost: two copies of the same field names and enums to keep in sync. `tests/test_schema.py` catches drift on the field names.
