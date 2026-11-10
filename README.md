# site-record

Turns a construction site's Telegram group into confirmed daily records and a delay-event register. Built for contractors in Cambodia. Output follows the CEIP Daily Log format.

Project context and rules: [CLAUDE.md](CLAUDE.md). Decisions: [docs/decisions/](docs/decisions/).

## Setup

Uses an Anaconda environment defined in `environment.yml`. Run from the repo root:

```bash
conda env create -f environment.yml
conda activate site-record
cp .env.example .env               # Windows: copy .env.example .env
pytest
```

After changing `environment.yml`: `conda env update -f environment.yml --prune`.

## Use (Phase 1, offline)

Export the group from Telegram Desktop: open the chat, menu > Export chat history, tick photos and files, format JSON. Then:

```bash
site-record ingest path/to/ChatExport_2026-11-10 --project PROJ-001
site-record days --project PROJ-001
```

`days` prints, per site day, how many messages, photos, voice notes and files arrived and from how many people.

Everything under `data/` stays on your machine and is never committed.
