"""
Pulls the most recent HN 'Ask HN: Who is Hiring?' thread via Algolia.
Parses top-level comments as individual job postings.
"""
import re
import requests
from datetime import datetime


HN_SEARCH = "https://hn.algolia.com/api/v1/search"
HN_ITEMS = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def _get_latest_who_is_hiring() -> int | None:
    params = {
        "query": "Ask HN: Who is Hiring?",
        "tags": "story,ask_hn",
        "hitsPerPage": 5,
    }
    try:
        resp = requests.get(HN_SEARCH, params=params, timeout=10)
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        for hit in hits:
            if "who is hiring" in hit.get("title", "").lower():
                return int(hit["objectID"])
    except Exception as e:
        print(f"[hn_hiring] search error: {e}")
    return None


def _parse_comment(text: str) -> tuple[str, str, str]:
    """Best-effort extraction of title, company, location from raw HN comment."""
    lines = [l.strip() for l in re.sub(r"<[^>]+>", "", text).split("\n") if l.strip()]
    first = lines[0] if lines else "Unknown Role"
    # Many HN posts start: "Company | Role | Location | ..."
    parts = [p.strip() for p in re.split(r"\s*[\|/]\s*", first)]
    company = parts[0] if parts else "Unknown"
    title = parts[1] if len(parts) > 1 else "Engineer"
    location = parts[2] if len(parts) > 2 else "Remote / Unknown"
    return title[:200], company[:200], location[:200]


def fetch() -> list[dict]:
    jobs = []
    story_id = _get_latest_who_is_hiring()
    if not story_id:
        return jobs
    try:
        story = requests.get(HN_ITEMS.format(story_id), timeout=10).json()
        kids = story.get("kids", [])[:60]  # cap at 60 comments
    except Exception as e:
        print(f"[hn_hiring] story fetch error: {e}")
        return jobs

    for kid_id in kids:
        try:
            item = requests.get(HN_ITEMS.format(kid_id), timeout=8).json()
            if item.get("deleted") or item.get("dead"):
                continue
            text = item.get("text", "")
            title, company, location = _parse_comment(text)
            posted_at = None
            ts = item.get("time")
            if ts:
                posted_at = datetime.fromtimestamp(ts)
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": f"https://news.ycombinator.com/item?id={kid_id}",
                "description": re.sub(r"<[^>]+>", "", text)[:1000],
                "tags": "hn-hiring",
                "source": "hn_hiring",
                "posted_at": posted_at,
            })
        except Exception as e:
            print(f"[hn_hiring] comment {kid_id} error: {e}")
    return jobs
