"""Probe the boards listed in scripts/probe_candidates.txt (from Simplify's apply links) with the same manners as the nightly job.
    python scripts/probe_candidates.py
Prints companies.yaml lines for boards that answer; writes them to probe_found.txt. Nothing in data/ is changed."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import probe_sources  # noqa: E402

LINE = re.compile(r'name: "(.*?)", ats: (\w+), board: "(.*?)"')
seen, guesses = set(), []
for line in ((Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "probe_candidates.txt")).read_text(encoding="utf-8").splitlines():
    m = LINE.search(line)
    if m and m.groups() not in seen:
        seen.add(m.groups())
        guesses.append(m.groups())
probe_sources.GUESSES = guesses
print(f"probing {len(guesses)} boards, about 1 second each", flush=True)
probe_sources.main()
