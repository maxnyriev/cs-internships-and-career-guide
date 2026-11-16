"""Fail loudly when the laptop's Workday/Oracle data is stale, so a silent laptop doesn't go unnoticed.

Runs as the Action's last step, after the board is published, so a stale laptop never blocks the cloud refresh.
A failed run emails the repo owner (GitHub's default), which is the alert.
"""
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import LOCAL, load_json  # noqa: E402

MAX_HOURS = 36  # one missed night is fine; two is not


def main():
    local = load_json(LOCAL, None)
    if not local:
        sys.exit("::error::data/local.json is missing: the laptop job has never pushed")
    fetched = datetime.fromisoformat(local["fetched_at"])
    hours = (datetime.now(timezone.utc) - fetched).total_seconds() / 3600
    n = len(local.get("rows", []))
    if hours > MAX_HOURS:
        sys.exit(f"::error::Laptop data is {hours:.0f} hours old (last run {local['fetched_at']}). "
                 f"{n} Workday/Oracle postings aren't being refreshed. Run scripts/local/nightly.ps1 or check Task Scheduler.")
    print(f"laptop data is {hours:.0f} hours old ({n} rows): OK")


if __name__ == "__main__":
    main()
