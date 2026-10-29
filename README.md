# JobPulse

An automated tech job aggregator that collects, deduplicates, and serves job postings from multiple public sources on a daily schedule.

## Features

- **Multi-source ingestion** — pulls from Remotive, Arbeitnow, and HackerNews *Who's Hiring* threads
- **Deduplication** — SHA-256 hash of title + company + URL prevents duplicate listings across sources and runs
- **Data normalization** — standardizes titles, companies, locations, and dates regardless of source format
- **REST API** — FastAPI backend with search, source filtering, and pagination
- **Dashboard** — dark-mode frontend with live search, source badges, and job counts
- **Automated scheduling** — APScheduler runs ingestion daily at 8 AM; GitHub Actions cron keeps the DB up to date in CI

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, APScheduler
- **Database:** SQLite (local) / PostgreSQL-ready
- **Scrapers:** Requests + custom parsers per source
- **CI:** GitHub Actions

## Project Structure

```
JobPulse/
├── .github/
│   └── workflows/
│       └── daily_ingest.yml   # Cron job: runs ingestion at 8 AM UTC daily
├── backend/
│   ├── main.py                # FastAPI app + scheduler
│   ├── database.py            # SQLAlchemy setup
│   ├── models.py              # Job model + dedup hash logic
│   ├── ingestion.py           # Pipeline orchestrator
│   ├── run_ingestion.py       # Standalone script for CI / manual runs
│   ├── requirements.txt
│   └── scrapers/
│       ├── remotive.py        # Remotive public API
│       ├── arbeitnow.py       # Arbeitnow public API
│       └── hn_hiring.py       # HN "Who is Hiring?" thread parser
└── frontend/
    └── index.html             # Single-page dashboard
```

## Getting Started

### 1. Install dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Open `http://localhost:8080` in your browser.

### 3. Trigger ingestion

Click **Run Ingestion** in the dashboard, or call the API directly:

```bash
curl -X POST http://localhost:8080/api/ingest
```

Or run the standalone script without starting the server:

```bash
python backend/run_ingestion.py
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/jobs` | List jobs with optional filters |
| `GET` | `/api/stats` | Total job count by source |
| `POST` | `/api/ingest` | Trigger the ingestion pipeline |

**Query parameters for `/api/jobs`:**

| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search title, company, or tags |
| `source` | string | Filter by source (`remotive`, `arbeitnow`, `hn_hiring`) |
| `location` | string | Filter by location |
| `limit` | int | Results per page (default 50, max 200) |
| `offset` | int | Pagination offset |

## Automated Ingestion (GitHub Actions)

The workflow at `.github/workflows/daily_ingest.yml` runs every day at 8 AM UTC. It:

1. Installs Python dependencies
2. Runs `backend/run_ingestion.py`
3. Commits the updated `jobpulse.db` back to the repo

You can also trigger it manually from the **Actions** tab in GitHub.

No API keys or secrets are required — all sources are public.

## Sources

| Source | Type | Coverage |
|--------|------|----------|
| [Remotive](https://remotive.com) | Public API | Remote tech jobs |
| [Arbeitnow](https://arbeitnow.com) | Public API | EU + global tech jobs |
| [HN Who's Hiring](https://news.ycombinator.com) | Thread parser | Startup / eng roles |
