"""Merge the laptop's data/local.json (Workday, Oracle) into postings.json. Run by the GitHub Action.

Laptop rows replace the previous laptop rows. If the laptop hasn't run for 3+ days,
its rows stay but show ⚠ (status "uncertain"), so the board degrades instead of breaking.
Postings the laptop closed (local.json "removed") are copied into removed.json, the one record of closed postings.
Duplicate postings (same company, title and location under different links) are merged here, at ingest,
so postings.json, the counts and the pages all agree.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import adapters  # noqa: E402
from common import LOCAL, POSTINGS, REMOVED, dedupe_rows, load_json, save_json  # noqa: E402

STALE_DAYS = 3


def main():
    local = load_json(LOCAL, None)
    if not local:
        print("no laptop data yet")
        return
    rows = [r for r in load_json(POSTINGS, []) if r.get("source") not in adapters.LOCAL]
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(local["fetched_at"])).days
    stale_since = local["fetched_at"][:10]
    for r in local["rows"]:
        if age >= STALE_DAYS:  # laptop off: rows show ⚠, and check_links drops them a week after the last laptop run
            r = {**r, "status": "uncertain", "uncertain_since": r.get("uncertain_since") or stale_since}
        rows.append(r)
    open_ids = {r["id"] for r in local["rows"]}
    removed = [r for r in load_json(REMOVED, []) if r["id"] not in open_ids]  # reopened on the laptop: no longer closed
    have = {(r["id"], r.get("removed_on")) for r in removed}
    added = [r for r in local.get("removed", []) if (r["id"], r.get("removed_on")) not in have and r["id"] not in open_ids]
    save_json(REMOVED, (removed + added)[-5000:])  # first, like fetch_ats: a crash never loses a closed row
    before = len(rows)
    rows = dedupe_rows(rows)
    save_json(POSTINGS, sorted(rows, key=lambda r: (r["company"].lower(), r["title"].lower())))
    print(f"merged {len(local['rows'])} laptop rows (fetched {age} day(s) ago); {before - len(rows)} duplicates merged")


if __name__ == "__main__":
    main()
