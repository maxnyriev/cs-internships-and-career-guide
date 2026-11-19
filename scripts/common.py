"""Shared helpers: paths, JSON/YAML I/O, URL keys, polite HTTP."""
import json
import os
import threading
import time
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib import robotparser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
POSTINGS = DATA / "postings.json"
REMOVED = DATA / "removed.json"
COMPANIES = DATA / "companies.yaml"
MANUAL = DATA / "manual.yaml"
LOCAL = DATA / "local.json"  # written only by the laptop job (Workday, Oracle)

BOT_NAME = "cs-internships-and-career-guide"
REPO_URL = "https://github.com/rohitpeets/cs-internships-and-career-guide"
USER_AGENT = f"{BOT_NAME}/1.0 (free student job board; contact: {REPO_URL})"
# Tracking parameters are matched by exact name (utm_* by prefix), so a job-id parameter
# that merely starts with "ref" or "source" (refNo=123, sourceId=9) is never stripped.
TRACKING_PREFIX = ("utm_",)
TRACKING = {"source", "src", "ref", "referrer", "gh_src", "lever-source", "lever-origin", "trk", "trackingid"}


TZ = ZoneInfo("America/Chicago")  # every date the board shows or compares is U.S. Central, not the runner's UTC


def today_date() -> date:
    return datetime.now(TZ).date()


def today() -> str:
    return today_date().isoformat()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def save_json(path: Path, obj) -> None:
    """Atomic write (temp file + rename), so a crash never leaves half a file. Lists are written one record per line,
    so the daily commit's diff is only the rows that changed."""
    if isinstance(obj, list):
        text = "[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in obj) + "\n]\n"
    else:
        text = json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=True) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    for attempt in range(5):  # Windows: antivirus or the search indexer can briefly lock the file, so the rename retries
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.3 * (attempt + 1))


def load_yaml(path: Path, default):
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8")) or default


def url_key(url: str) -> str:
    """Apply URL without tracking parameters or a trailing slash; job-id parameters are kept.
    Scheme and host are lowercased (they are case-insensitive); the path and query keep their case,
    because some boards put a case-sensitive job id there and two jobs must not share one key."""
    s = urlsplit(url.strip())
    q = [(k, v) for k, v in parse_qsl(s.query) if k.lower() not in TRACKING and not k.lower().startswith(TRACKING_PREFIX)]
    return urlunsplit((s.scheme.lower(), s.netloc.lower(), s.path.rstrip("/"), urlencode(q), ""))


def dedupe_rows(rows):
    """Same company + title + location kept once (companies often post one job under several links or career sites).
    An open copy beats an unverified one; the earliest first_seen is kept, so the job doesn't look newer than it is."""
    best = {}
    for r in rows:
        k = (r["company"].lower().strip(), " ".join(r["title"].lower().split()), " ".join((r.get("location") or "").lower().split()))
        cur = best.get(k)
        if cur is None:
            best[k] = r
            continue
        first = min(cur["first_seen"], r["first_seen"])
        rank = lambda x: (x.get("status") == "uncertain", x.get("misses", 0), x["first_seen"])  # noqa: E731
        win = r if rank(r) < rank(cur) else cur
        best[k] = {**win, "first_seen": first}
    return list(best.values())


class Blocked(Exception):
    """The site said no: robots.txt disallows the path, or a robots-checked site answered 401/403. We stop; we never work around it."""


class Unavailable(Exception):
    """Couldn't ask politely today (robots.txt unreachable or 5xx, or a public API answered 401/403).
    Counted as a failed board for this run only, never recorded as a permanent block."""


RETRY_STATUS = (429, 500, 502, 503, 504)


_ROBOTS: dict = {}
_ROBOTS_LOCK = threading.Lock()
_HOST_LAST: dict = {}
_HOST_GAP: dict = {}  # per-host Crawl-delay from robots.txt, when it asks for more than the default gap
_HOST_LOCKS: dict = {}
_LOCKS_LOCK = threading.Lock()


class Http:
    """requests session; every Http object shares one pacing clock per host, so boards on the
    same host (boards-api.greenhouse.io) never go back-to-back. 429/5xx, timeouts and dropped
    connections are retried with backoff, so one blip doesn't fail a board for the day."""

    def __init__(self, gap: float = 1.0, timeout: float = 20.0, retries: int = 3, check_robots: bool = False):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = USER_AGENT
        self.gap, self.timeout, self.retries, self.check_robots = gap, timeout, retries, check_robots

    def robots_allow(self, url: str) -> bool:
        """robots.txt for the URL's site, read once per run (RFC 9309): 4xx means allowed;
        401/403 on robots.txt itself means everything is off limits; 5xx or unreachable means
        "assume disallowed" for this run, raised as Unavailable so it isn't recorded as a permanent block.
        A Crawl-delay for our agent (or *) raises this host's gap."""
        s = urlsplit(url)
        root = f"{s.scheme}://{s.netloc}"
        with _ROBOTS_LOCK:
            rp = _ROBOTS.get(root)
        if rp is None:
            rp = robotparser.RobotFileParser()
            try:
                self._wait_turn(s.netloc)
                r = self.s.get(root + "/robots.txt", timeout=self.timeout)
                if r.status_code in (401, 403):
                    rp.disallow_all = True
                elif r.status_code >= 500:
                    rp = "unavailable"
                elif r.status_code >= 400:
                    rp.allow_all = True
                else:
                    rp.parse(r.text.splitlines())
            except requests.RequestException:
                rp = "unavailable"
            with _ROBOTS_LOCK:
                _ROBOTS[root] = rp
        if rp == "unavailable":
            raise Unavailable(f"robots.txt for {s.netloc} unreachable or 5xx; not fetching today")
        delay = rp.crawl_delay(BOT_NAME)
        if delay:
            with _LOCKS_LOCK:
                _HOST_GAP[s.netloc] = max(_HOST_GAP.get(s.netloc, 0), min(float(delay), 30.0))
        return rp.can_fetch(BOT_NAME, url)

    def _wait_turn(self, host: str) -> None:
        with _LOCKS_LOCK:
            lock = _HOST_LOCKS.setdefault(host, threading.Lock())
        with lock:
            wait = max(self.gap, _HOST_GAP.get(host, 0)) - (time.monotonic() - _HOST_LAST.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            _HOST_LAST[host] = time.monotonic()

    def _call(self, method: str, url: str, **kw) -> requests.Response:
        host = urlsplit(url).netloc
        if self.check_robots and not self.robots_allow(url):
            raise Blocked(f"robots.txt disallows {urlsplit(url).path}")
        for attempt in range(self.retries + 1):
            self._wait_turn(host)
            try:
                r = self.s.request(method, url, timeout=self.timeout, **kw)  # sleeping happens outside the host lock
            except (requests.ConnectionError, requests.Timeout):
                if attempt == self.retries:
                    raise
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code in (401, 403):
                # A site we check robots.txt for is saying no: respect it. A published public API (Greenhouse, Lever...)
                # answering 403 is usually a firewall hiccup, so it only fails this run.
                raise (Blocked if self.check_robots else Unavailable)(f"HTTP {r.status_code} from {host}")
            if r.status_code not in RETRY_STATUS or attempt == self.retries:
                return r
            try:
                delay = max(0.0, min(float(r.headers.get("Retry-After", "")), 60))
            except ValueError:
                delay = 5 * (attempt + 1)
            time.sleep(delay)
        return r

    def get(self, url: str, **kw) -> requests.Response:
        return self._call("GET", url, **kw)

    def post(self, url: str, **kw) -> requests.Response:
        return self._call("POST", url, **kw)
