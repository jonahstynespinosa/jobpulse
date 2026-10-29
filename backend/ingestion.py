from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import Job
from database import SessionLocal
from scrapers import remotive, arbeitnow, hn_hiring


SCRAPERS = [remotive, arbeitnow, hn_hiring]


def _ingest_batch(db: Session, raw_jobs: list[dict]) -> tuple[int, int]:
    added, skipped = 0, 0
    for j in raw_jobs:
        if not j.get("title") or not j.get("company") or not j.get("url"):
            skipped += 1
            continue
        dedup_hash = Job.make_hash(j["title"], j["company"], j["url"])
        job = Job(dedup_hash=dedup_hash, **{k: v for k, v in j.items()})
        db.add(job)
        try:
            db.commit()
            added += 1
        except IntegrityError:
            db.rollback()
            skipped += 1
    return added, skipped


def run_ingestion() -> dict:
    db = SessionLocal()
    results = {}
    try:
        for scraper in SCRAPERS:
            name = scraper.__name__.split(".")[-1]
            print(f"[ingestion] running {name}...")
            raw = scraper.fetch()
            added, skipped = _ingest_batch(db, raw)
            results[name] = {"fetched": len(raw), "added": added, "skipped": skipped}
            print(f"[ingestion] {name}: fetched={len(raw)} added={added} skipped={skipped}")
    finally:
        db.close()
    return results
