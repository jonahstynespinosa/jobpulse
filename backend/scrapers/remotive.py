import requests
from datetime import datetime
from dateutil import parser as dateparser


BASE_URL = "https://remotive.com/api/remote-jobs"
CATEGORIES = ["software-dev", "data", "devops-sysadmin"]


def fetch() -> list[dict]:
    jobs = []
    for cat in CATEGORIES:
        try:
            resp = requests.get(BASE_URL, params={"category": cat}, timeout=10)
            resp.raise_for_status()
            for j in resp.json().get("jobs", []):
                posted_at = None
                try:
                    posted_at = dateparser.parse(j.get("publication_date", ""))
                except Exception:
                    pass
                jobs.append({
                    "title": j.get("title", "").strip(),
                    "company": j.get("company_name", "").strip(),
                    "location": j.get("candidate_required_location") or "Remote",
                    "url": j.get("url", ""),
                    "description": (j.get("description") or "")[:1000],
                    "tags": ", ".join(j.get("tags", []))[:500],
                    "source": "remotive",
                    "posted_at": posted_at,
                })
        except Exception as e:
            print(f"[remotive] error fetching {cat}: {e}")
    return jobs
