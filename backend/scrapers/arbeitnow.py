import requests
from datetime import datetime


BASE_URL = "https://www.arbeitnow.com/api/job-board-api"


def fetch() -> list[dict]:
    jobs = []
    try:
        resp = requests.get(BASE_URL, timeout=10)
        resp.raise_for_status()
        for j in resp.json().get("data", []):
            posted_at = None
            ts = j.get("created_at")
            if ts:
                try:
                    posted_at = datetime.fromtimestamp(ts)
                except Exception:
                    pass
            jobs.append({
                "title": j.get("title", "").strip(),
                "company": j.get("company_name", "").strip(),
                "location": j.get("location") or "Remote",
                "url": j.get("url", ""),
                "description": (j.get("description") or "")[:1000],
                "tags": ", ".join(j.get("tags", []))[:500],
                "source": "arbeitnow",
                "posted_at": posted_at,
            })
    except Exception as e:
        print(f"[arbeitnow] error: {e}")
    return jobs
