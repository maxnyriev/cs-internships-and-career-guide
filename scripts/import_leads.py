"""Turn a CSV of leads into data/manual.yaml entries, checking each lead's own page first.
    python scripts/import_leads.py private/leads.csv [--days 14] [--no-verify] [--limit N] [--workers 6]

CSV columns: company, title, location, url (apply_url also works). Run it on the laptop, then commit data/manual.yaml.
For each lead the employer's page is read with the board's polite fetcher (robots.txt, waits, no logins):
    verified    the page loads and shows the job's title      -> added as a normal row
    unverified  blocked, needs JavaScript, or no title found  -> added with the ⚠ warning
    dead        404/410, "no longer accepting", past validThrough -> not added (and removed if it was there)
Every entry gets `expires` = today + --days. A lead that shows up in a later import gets its date renewed;
one that doesn't just runs out, and check_links.py still closes any that go 404 in the meantime.
"""
import argparse
import csv
import html
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_links import CLOSED_TEXT, visible  # noqa: E402
from common import MANUAL, POSTINGS, Http, load_json, today_date, url_key  # noqa: E402

VALID_THROUGH = re.compile(r'"validThrough"\s*:\s*"(\d{4}-\d{2}-\d{2})')


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def page_state(status: int, text: str, title: str, today: date) -> str:
    if status in (404, 410):
        return "dead"
    if status >= 400:
        return "unverified"
    if CLOSED_TEXT.search(visible(text[:400000])):
        return "unverified"  # hint only: live jobs on some sites carry hidden "no longer available" markup
    m = VALID_THROUGH.search(text)
    if m and m.group(1) < today.isoformat():
        return "dead"
    t = norm(html.unescape(title))
    body = norm(re.sub(r"<[^>]+>", " ", html.unescape(text[:400000])))
    words = [w for w in t.split() if len(w) > 3]
    if t and (t in body or (words and all(w in body for w in words))):
        return "verified"
    return "unverified"


def merge(existing: list, leads: list, today: date, days: int) -> list:
    expires = (today + timedelta(days=days)).isoformat()
    out = {url_key(m["url"]): m for m in existing}
    for ld in leads:
        key = url_key(ld["url"])
        if ld["state"] == "dead":
            out.pop(key, None)
            continue
        entry = {"company": ld["company"], "title": ld["title"], "url": ld["url"]}
        if ld.get("location"):
            entry["location"] = ld["location"]
        entry["expires"] = expires
        if ld["state"] == "unverified":
            entry["unverified"] = True
        merged = {**out.get(key, {}), **entry}
        if ld["state"] != "unverified":  # confirmed now: the warning goes away
            merged.pop("unverified", None)
        out[key] = merged
    return list(out.values())


def render(header: str, items: list) -> str:
    def val(v):
        return "true" if v is True else json.dumps(v, ensure_ascii=False)
    lines = [f"  - {{{', '.join(f'{k}: {val(v)}' for k, v in m.items())}}}" for m in items]
    return header + "postings:\n" + ("\n".join(lines) + "\n" if lines else " []\n")


INVISIBLE = re.compile("[\u200b-\u200f\u2060\ufeff]")  # zero-width characters some career sites put in titles


def clean(s: str) -> str:
    return INVISIBLE.sub("", s or "").strip()


def https_url(u: str) -> str:
    """The board stores https links only (the schema requires it); almost every careers host redirects http there anyway."""
    u = clean(u)
    return "https://" + u[len("http://"):] if u.startswith("http://") else u


def read_leads(path: Path) -> list:
    with open(path, newline="", encoding="utf-8") as f:
        return [{"company": clean(r["company"]), "title": clean(r["title"]), "location": clean(r.get("location")),
                 "url": https_url(r.get("url") or r.get("apply_url"))} for r in csv.DictReader(f)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--no-verify", action="store_true", help="skip the page check: every lead is added with the warning")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=6, help="sites checked at once; each site is still paced 2 seconds apart")
    a = ap.parse_args()
    sys.stdout.reconfigure(errors="replace")  # a Windows console can't print every character; never crash on one
    import yaml
    leads = read_leads(Path(a.csv))[: a.limit]
    on_feed = {r["id"] for r in load_json(POSTINGS, []) if r.get("source") != "manual"}
    leads = [ld for ld in leads if ld["url"] and url_key(ld["url"]) not in on_feed]  # a company feed already carries these
    http = Http(gap=2.0, timeout=20, retries=1, check_robots=True)  # one clock per site, shared by every worker

    def check(ld):
        if a.no_verify:
            return "unverified"
        try:
            r = http.get(ld["url"], allow_redirects=True)
            return page_state(r.status_code, r.text, ld["title"], today_date())
        except Exception:  # Blocked, robots.txt, timeouts: still a lead, but we couldn't check it
            return "unverified"

    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i, (ld, state) in enumerate(zip(leads, pool.map(check, leads)), 1):
            ld["state"] = state
            print(f"[{i}/{len(leads)}] {state:10} {ld['company'][:28]:28} {ld['title'][:60]}", flush=True)
    text = MANUAL.read_text(encoding="utf-8")
    header = text.split("postings:")[0]
    existing = (yaml.safe_load(text) or {}).get("postings") or []
    MANUAL.write_text(render(header, merge(existing, leads, today_date(), a.days)), encoding="utf-8")
    counts = {s: sum(1 for ld in leads if ld["state"] == s) for s in ("verified", "unverified", "dead")}
    print(f"done: {counts}; data/manual.yaml updated. Review it, then run the tests and commit.")


if __name__ == "__main__":
    main()
