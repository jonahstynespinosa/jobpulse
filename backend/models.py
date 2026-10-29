import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dedup_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    company: Mapped[str] = mapped_column(String(200))
    location: Mapped[str] = mapped_column(String(200), default="Remote")
    url: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(50))
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @staticmethod
    def make_hash(title: str, company: str, url: str) -> str:
        raw = f"{title.lower().strip()}|{company.lower().strip()}|{url.strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()
