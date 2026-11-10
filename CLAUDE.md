# CLAUDE.md

Read this first in every session. It holds the decisions made before this repo existed (planning chat with Vathna, 10 Nov 2026). Detailed reasons are in `docs/decisions/`.

## What this is

site-record reads a construction project's existing Telegram group and turns it into confirmed daily site records plus a register of delay events that can later be used as claim evidence. The target market is contractors in Phnom Penh, Cambodia, where Telegram is the main business messaging app. Owner: Vathna (construction PM background, FIDIC contracts, Python). This is a business project, not the thesis.

The key product idea: site staff change nothing. They keep posting photos and messages to their group as they already do. The system captures everything, drafts the day's record, and asks the site engineer to fill gaps in the evening.

## Relationship to CEIP

`suyvathna/CEIP` (Construction Evidence Intelligence Platform) already models the Cambodian site diary (DailyLog with manpower, equipment, delivery, inspection, HSE, visitor and rain-record tables), Evidence, FIDIC event types, claims and notice deadlines. Its weak point is input: everything is typed in by hand.

This repo is that missing input layer, kept separate and lightweight on purpose. `schema.DailyRecord` copies the shape of CEIP's `DailyLogCreate`, and `ceip_enums.py` copies CEIP's `EventType` and `PhotoCategory`, so records can be posted into CEIP later without a rewrite. Do not add a dependency on CEIP's stack (Postgres, MinIO, FastAPI, React). See `docs/ceip-mapping.md`.

## Scope of v1

In: Khmer or English text, photos with captions, Excel attachments.
Stored and listed but content not read: voice notes, PDFs, Word files, video.
Out: voice transcription, web dashboard, user accounts or multiple companies, weekly/monthly reports, schedule integration.

## Pipeline

```
Telegram export JSON (phase 1) ─┐
Telegram webhook (phase 2) ─────┴─► 1 ingest → models.Message
                                    2 store    (append-only evidence)
                                    3 normalize (plain Python)
                                    4 extract  (LLM → schema.MessageExtraction)
                                    5 assemble (plain Python → schema.DailyRecord)
                                    6 confirm  (site engineer fills gaps)
                                    7 report   (Excel daily report, delay register)
```

Phase 1 runs offline on a Telegram Desktop chat export from a past project. Phase 2 adds the live bot (python-telegram-bot, webhook) as a second ingest source. Nothing after step 1 may know which source a message came from.

## Rules that must not be broken

1. The evidence store is append-only. SQLite triggers enforce it. Never add a code path that edits or deletes raw messages.
2. Every extracted fact keeps the message id(s) it came from. No orphan facts.
3. The LLM interprets meaning only. Anything deterministic (Khmer digits ០-៩ to 0-9, timezones, role mapping, Excel parsing) is done in code before the LLM sees the message.
4. Never estimate quantities, worker counts or progress % from a photo. Numbers come from text only.
5. FIDIC event types from the LLM are candidates until the engineer confirms them.
6. Group messages by Phnom Penh calendar day (`normalize.site_date`), never by UTC date.
7. Prompts live in `prompts/extract_vN.md`, never inline in code. Store the prompt version with each extraction.
8. Real client chat exports never go through the Gemini free tier (Google uses free-tier content to improve its products) and never get committed. `data/` is gitignored.

## Environment

Always work inside the Anaconda environment `site-record` defined in `environment.yml` (`conda env create -f environment.yml`, then `conda activate site-record`). Don't create venvs or install packages globally. New dependencies go into `environment.yml` (and `pyproject.toml` if the package needs them at runtime), then `conda env update -f environment.yml --prune`.

## Stack

Python 3.12, Pydantic, SQLite plus a media folder, Gemini (`google-genai`, paid tier for real data, model in `.env`), openpyxl. Phase 2: python-telegram-bot on a small VPS.

## Status (10 Nov 2026)

Built and tested (`pytest`, 10 tests passing): Telegram export parser, normaliser, append-only evidence store with SHA-256 file hashing, record schema, CLI `ingest` and `days`.

Stubs with written contracts: `extract.py`, `assemble.py`, `report.py`. Draft prompt: `prompts/extract_v1.md`.

## Next steps, in order

1. Get one real Telegram Desktop JSON export of a past site group from a contractor contact. Run `site-record ingest` and `site-record days`. Check the export format against the notes in `ingest/telegram_export.py` and record any differences in `docs/decisions/`.
2. Read 50 real messages by hand. Adjust `schema.py` and `prompts/extract_v1.md` to what sites actually post.
3. Build `extract.py` with Gemini structured output. First check whether the discriminated union in `MessageExtraction.items` is accepted; if not, flatten it (see the docstring).
4. Measure extraction on those 50 messages against Vathna's own reading before building anything else.
5. Build `assemble.py`, then the Excel daily report and delay register in `report.py`.
6. Demo: show the contact their own finished project rebuilt as daily records and a delay register.
7. Only after the demo lands: Phase 2 live bot.

## Money

Before any step that can cost money (paid API calls, hosting, paid packages or services), say so up front with a rough cost estimate and wait for Vathna's go. The Gemini key currently lives in the Google Cloud project he also uses for his thesis. Whether calls are billed depends on whether that project has billing linked (AI Studio > API keys shows the tier per project). Assume billed until he confirms otherwise.

## Working style

Vathna wants direct answers, code with the reasoning behind design choices, and explicit confidence labels (verified, inferred, guessed). Push back when an idea is weak. Record any non-obvious choice in `docs/decisions/` as a short numbered note.
