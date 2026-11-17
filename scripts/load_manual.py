"""Merge data/manual.yaml (postings added by maintainers) into postings.json.

manual.yaml:
  postings:
    - company: Example Corp
      title: Software Engineering Intern
      url: https://example.com/jobs/123
      location: Houston, TX          # optional
      section: internship            # optional: internship | new_grad | early
      evidence: "Open to first- and second-year students."   # required for early: the sentence from the program page
      notes: confirmed open by email      # optional, for maintainers only: never shown and never tagged
      expires: "2026-12-01"          # optional: the row leaves the board after this day unless a later import renews it
      unverified: true               # optional: the posting's own page couldn't confirm it, so the row shows ⚠
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from classify import section, tags  # noqa: E402
from common import MANUAL, POSTINGS, load_json, load_yaml, save_json, today, today_date, url_key  # noqa: E402


def main():
    items = load_yaml(MANUAL, {"postings": []}).get("postings") or []
    rows = {r["id"]: r for r in load_json(POSTINGS, [])}
    live = set()
    for m in items:
        if m.get("expires") and str(m["expires"])[:10] < today():  # past its date: skipped here, so the cleanup below removes the row
            continue
        rid = url_key(m["url"])
        live.add(rid)
        t, ev = tags("", m.get("location", ""))  # notes are private: only the location can tag a manual row (remote)
        if m.get("section") == "early":  # an early program shows the page's own eligibility sentence, like fetched ones
            if not m.get("evidence"):
                sys.exit(f"manual.yaml: {m['company']} is marked early but has no evidence sentence")
            ev = {**ev, "early": m["evidence"]}
        old = rows.get(rid, {})
        rows[rid] = {**old, "id": rid, "company": m["company"], "title": m["title"], "url": m["url"],
                     "location": m.get("location", ""), "source": "manual",
                     "section": m.get("section") or section(m["title"]) or "internship",
                     "tags": t, "tag_evidence": ev,
                     "status": "uncertain" if m.get("unverified") else ("open" if old.get("unverified") else old.get("status", "open")),
                     "misses": old.get("misses", 0),
                     "first_seen": old.get("first_seen", today()), "last_seen": today()}
        if m.get("unverified"):
            rows[rid].update(unverified=True, uncertain_since=None)  # no 7-day clock for these: expires decides
        else:
            rows[rid].pop("unverified", None)
    # a row deleted from manual.yaml leaves the board
    for rid in [k for k, r in rows.items() if r.get("source") == "manual" and k not in live]:
        del rows[rid]
    save_json(POSTINGS, sorted(rows.values(), key=lambda r: (r["company"].lower(), r["title"].lower())))
    print(f"manual postings: {len(live)}")


if __name__ == "__main__":
    main()
