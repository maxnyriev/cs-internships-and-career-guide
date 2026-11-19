"""Measure how accurate the live board is, on a reproducible random sample.

    python scripts/audit_sample.py              # 200 rows, seed 1, writes docs/AUDIT.md
    python scripts/audit_sample.py --n 50 --seed 7 --out -

Every check re-runs the real classifier, so the numbers move when the rules move. The tag check
re-reads the sentence the board saved as its evidence: if that sentence no longer produces the tag,
either the evidence is wrong or a rule changed, and a student is being shown a claim nothing backs.
Nothing here judges whether a job is genuinely CS/CE work; the sample list at the end is for that,
by hand.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import classify  # noqa: E402
from common import POSTINGS, load_json  # noqa: E402

CHECKS = {
    "us_location": "location is in the U.S.",
    "title_relevant": "title still passes the CS/CE title rules",
    "term_current": "title is not for a term that has passed",
    "section_right": "internship / new grad / early matches the title",
    "tag_backed": "every tag is reproduced by the sentence saved as its evidence",
}


def audit_row(r):
    """-> {check: (ok, detail)} for one posting."""
    out = {}
    loc = r.get("location") or ""
    out["us_location"] = (classify.us_job(loc), loc)
    out["title_relevant"] = (classify.keep_title(r["title"]), r["title"])
    out["term_current"] = (not classify.expired_term(r["title"]), r["title"])
    want = classify.section(r["title"])
    out["section_right"] = (want == r.get("section"), f'{r.get("section")} vs {want}')

    bad = []
    ev = r.get("tag_evidence") or {}
    for name, value in (r.get("tags") or {}).items():
        # sponsor=False is a real claim ("this employer does not sponsor") and the one students lean on
        # hardest, so it gets checked. Elsewhere False just means the tag is absent.
        if value is None or name == "remote" or (value is False and name != "sponsor"):
            continue
        # the clearance level is read out of the same sentence the clearance tag saved
        sentence = ev.get("clearance" if name == "clearance_level" else name)
        if not sentence:
            bad.append(f"{name}={value} has no evidence")
            continue
        if name == "clearance_level":
            again = classify.clearance_level(sentence)
        else:
            again = classify.tags(sentence)[0].get(name)
        if again != value and not (value is True and again):
            bad.append(f"{name}={value} but its evidence now reads {again}")
    out["tag_backed"] = (not bad, "; ".join(bad))
    return out


def report(rows, sample, results):
    lines = [f"# Accuracy audit, {len(sample)} random postings of {len(rows)}", ""]
    failures = {}
    lines += ["| Check | Wrong | Rate |", "|---|---|---|"]
    for key, label in CHECKS.items():
        bad = [(r, d[key][1]) for r, d in results if not d[key][0]]
        failures[key] = bad
        lines.append(f"| {label} | {len(bad)} | {len(bad) / len(sample):.1%} |")
    clean = sum(1 for _, d in results if all(v[0] for v in d.values()))
    lines += ["", f"**{clean} of {len(sample)} rows passed every check ({clean / len(sample):.1%}).**", ""]
    for key, bad in failures.items():
        if not bad:
            continue
        lines += [f"## Wrong: {CHECKS[key]}", ""]
        for r, detail in bad[:25]:
            lines.append(f"- [{r['company']} — {r['title']}]({r['url']}) — {detail}")
        if len(bad) > 25:
            lines.append(f"- ...and {len(bad) - 25} more")
        lines.append("")
    lines += ["## To judge by hand", "",
              "Is each of these really a CS or CE job a student could do? Mark the ones that aren't.", ""]
    for r, _ in results[:25]:
        lines.append(f"- [ ] [{r['company']} — {r['title']}]({r['url']}) — {r.get('location')}")
    return lines


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=200)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--out", default="docs/AUDIT.md", help="file to write, or - for stdout only")
    a = p.parse_args()

    rows = [r for r in load_json(POSTINGS, []) if r.get("status") != "removed"]
    if not rows:
        sys.exit("no postings to audit")
    sample = random.Random(a.seed).sample(rows, min(a.n, len(rows)))
    results = [(r, audit_row(r)) for r in sample]
    lines = report(rows, sample, results)
    lines.insert(2, f"Reproduce with `python scripts/audit_sample.py --n {a.n} --seed {a.seed}`.\n")

    print("\n".join(lines[:11]))
    if a.out != "-":
        Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
