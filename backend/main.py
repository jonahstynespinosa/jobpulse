from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from apscheduler.schedulers.background import BackgroundScheduler

from database import init_db, get_session
from models import Job
from ingestion import run_ingestion

import os


scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Schedule daily ingestion at 8 AM
    scheduler.add_job(run_ingestion, "cron", hour=8, minute=0, id="daily_ingest")
    scheduler.start()
    print("[jobpulse] scheduler started — daily ingestion at 08:00")
    yield
    scheduler.shutdown()


app = FastAPI(title="JobPulse", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/api/jobs")
def get_jobs(
    q: Optional[str] = Query(None, description="Search title, company, tags"),
    source: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_session),
):
    query = db.query(Job)
    if q:
        term = f"%{q}%"
        query = query.filter(
            or_(
                Job.title.ilike(term),
                Job.company.ilike(term),
                Job.tags.ilike(term),
            )
        )
    if source:
        query = query.filter(Job.source == source)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    total = query.count()
    jobs = query.order_by(desc(Job.ingested_at)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "url": j.url,
                "tags": j.tags,
                "source": j.source,
                "posted_at": j.posted_at.isoformat() if j.posted_at else None,
                "ingested_at": j.ingested_at.isoformat(),
            }
            for j in jobs
        ],
    }


@app.get("/api/stats")
def get_stats(db: Session = Depends(get_session)):
    from sqlalchemy import func
    total = db.query(Job).count()
    source_counts = (
        db.query(Job.source, func.count(Job.id).label("count"))
        .group_by(Job.source)
        .all()
    )
    return {
        "total_jobs": total,
        "by_source": {s: c for s, c in source_counts},
    }


@app.post("/api/ingest")
def trigger_ingest():
    """Manually trigger the ingestion pipeline."""
    results = run_ingestion()
    return {"status": "ok", "results": results}


@app.get("/", include_in_schema=False)
def serve_frontend():
    index = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
