"""Safety rules from docs/WRITEUP.md: closing, gone boards, the failure threshold, the shrink guard, laptop staleness."""
import json
import subprocess
import sys
from datetime import date, timedelta

import pytest

import adapters
import build_readme
import check_links
import classify
import fetch_ats
import merge_local
import validate


def job(n):
    return {"title": f"Software Engineering Intern {n}", "url": f"https://x.com/jobs/{n}", "location": "Austin, TX", "text": ""}


@pytest.fixture
def board(tmp_path, monkeypatch):
    """A one-company world: companies.yaml with board 'acme', fake greenhouse adapter, temp data files."""
    comp = tmp_path / "companies.yaml"
    comp.write_text("companies:\n  - {name: Acme, ats: greenhouse, board: acme}\n")
    for name, path in (("COMPANIES", comp), ("POSTINGS", tmp_path / "postings.json"), ("REMOVED", tmp_path / "removed.json"),
                       ("BLOCKED", tmp_path / "blocked.json")):
        monkeypatch.setattr(fetch_ats, name, path)
    state = {"jobs": [job(1), job(2)], "error": None}

    def fake(b, http):
        if state["error"]:
            raise state["error"]
        return adapters.Jobs(state["jobs"])
    monkeypatch.setitem(adapters.CLOUD, "greenhouse", fake)
    monkeypatch.setattr(sys, "argv", ["fetch_ats.py", "--cloud"])

    def run(day):
        monkeypatch.setattr(fetch_ats, "today", lambda: day)
        fetch_ats.main()
        return {r["title"]: r for r in json.loads((tmp_path / "postings.json").read_text())}
    return state, run


def test_closes_after_two_days_missing_not_two_runs(board):
    state, run = board
    run("2026-11-01")
    state["jobs"] = [job(1)]
    run("2026-11-02")
    rows = run("2026-11-02")  # a second run the same day is not a second strike
    assert "Software Engineering Intern 2" in rows
    rows = run("2026-11-03")
    assert "Software Engineering Intern 2" not in rows and "Software Engineering Intern 1" in rows


def test_gone_board_flags_rows_instead_of_closing(board):
    state, run = board
    run("2026-11-01")
    state["error"] = adapters.BoardGone("acme: HTTP 404")
    run("2026-11-02")
    rows = run("2026-11-03")
    assert len(rows) == 2 and all(r["status"] == "uncertain" for r in rows.values())


def test_suddenly_empty_feed_does_not_close(board):
    state, run = board
    run("2026-11-01")
    state["jobs"] = []
    run("2026-11-02")
    rows = run("2026-11-03")
    assert len(rows) == 2


def test_failed_run_saves_nothing(board, tmp_path):
    state, run = board
    run("2026-11-01")
    before = (tmp_path / "postings.json").read_text()
    state["error"] = RuntimeError("network down")
    with pytest.raises(SystemExit):
        run("2026-11-02")
    assert (tmp_path / "postings.json").read_text() == before


def test_404_raises_board_gone():
    class R:
        status_code = 404
    class H:
        def get(self, *a, **k):
            return R()
    for name in ("greenhouse", "lever", "ashby", "smartrecruiters"):
        with pytest.raises(adapters.BoardGone):
            adapters.CLOUD[name]("old-slug", H())


def test_uncertain_rows_expire_after_a_week(tmp_path, monkeypatch):
    old = (date.today() - timedelta(days=8)).isoformat()
    rows = [{"id": "a", "url": "u", "source": "workday", "status": "uncertain", "uncertain_since": old},
            {"id": "b", "url": "u", "source": "workday", "status": "open"}]
    p, rm = tmp_path / "p.json", tmp_path / "r.json"
    p.write_text(json.dumps(rows))
    monkeypatch.setattr(check_links, "POSTINGS", p)
    monkeypatch.setattr(check_links, "REMOVED", rm)
    monkeypatch.setattr(sys, "argv", ["check_links.py", "--stale-only"])
    check_links.main()
    assert [r["id"] for r in json.loads(p.read_text())] == ["b"]


def test_stale_laptop_rows_marked_uncertain(tmp_path, monkeypatch):
    p, loc = tmp_path / "p.json", tmp_path / "l.json"
    p.write_text("[]")
    loc.write_text(json.dumps({"fetched_at": "2026-01-01T00:00:00+00:00", "rows": [{"id": "a", "company": "X", "title": "t", "source": "workday"}]}))
    monkeypatch.setattr(merge_local, "POSTINGS", p)
    monkeypatch.setattr(merge_local, "LOCAL", loc)
    merge_local.main()
    r = json.loads(p.read_text())[0]
    assert r["status"] == "uncertain" and r["uncertain_since"] == "2026-01-01"


def test_manual_early_program_keeps_its_section(tmp_path, monkeypatch):
    import load_manual
    man, p = tmp_path / "m.yaml", tmp_path / "p.json"
    man.write_text('postings:\n  - {company: X, title: "Explore Program", url: "https://x.com/p", section: early,'
                   ' evidence: "Open to first- and second-year students."}\n')
    p.write_text("[]")
    monkeypatch.setattr(load_manual, "MANUAL", man)
    monkeypatch.setattr(load_manual, "POSTINGS", p)
    load_manual.main()
    r = json.loads(p.read_text())[0]
    assert r["section"] == "early" and r["tag_evidence"]["early"].startswith("Open to first")
    man.write_text('postings:\n  - {company: X, title: "Explore", url: "https://x.com/p", section: early}\n')
    with pytest.raises(SystemExit):
        load_manual.main()


def test_shrink_guard_uses_7_commit_high_and_reset(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "data").mkdir()
    g = lambda *a: subprocess.run(["git", *a], check=True, capture_output=True)
    g("init", "-q")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    for n, msg in ((100, "a"), (60, "b"), (40, "c")):
        (tmp_path / "data/postings.json").write_text(json.dumps([{}] * n))
        g("add", ".")
        g("commit", "-qm", msg)
    assert validate.previous_count() == 100  # 40 now is under half of 100 even though the last step was 60 -> 40
    (tmp_path / "data/postings.json").write_text(json.dumps([{}] * 30))
    g("add", ".")
    g("commit", "-qm", "stricter filter [reset-baseline]")
    assert validate.previous_count() == 30


def test_us_job_locations():
    assert classify.us_job("Vienna, VA, United States")
    assert classify.us_job("Remote - US; London")
    assert not classify.us_job("Blumenau, SC, Brazil")
    assert not classify.us_job("Penang, Malaysia")
    assert not classify.us_job("CAD Remote – ON")


def test_board_dedupes():
    a = {"company": "T-Mobile", "title": "SWE Intern", "location": "Bellevue, WA", "first_seen": "2026-11-02"}
    b = {**a, "first_seen": "2026-11-01"}
    assert build_readme.dedupe([a, b]) == [b]


def test_new_this_week_always_lists_jobs():
    # a busy week (over 150 new rows) used to show no table at all
    today = date.today().isoformat()
    new = [{"company": f"Co{i}", "title": "SWE Intern", "location": "Austin, TX", "url": f"https://x.com/{i}",
            "first_seen": today, "posted": today, "section": "internship"} for i in range(200)]
    out = build_readme.new_section(new)
    assert out.count("](https://x.com/") == 75
    assert "200 postings were posted this week" in out  # the footer counts all of them, not just the 75 shown


def test_untrusted_text_cannot_inject_markdown_or_html():
    evil = 'Software Intern](https://evil.example/login) [Apply <img src=x onerror=alert(1)> | x\r\r# Fake'
    out = build_readme.text(evil)
    assert "](" not in out and "<img" not in out and "|" not in out and "\n" not in out and "\r" not in out


def test_only_plain_http_links():
    assert build_readme.safe_url("javascript:alert(1)") is None
    assert build_readme.safe_url("https://x.com/a b") is None
    assert build_readme.safe_url("https://x.com/jobs/1\n## Urgent") is None
    assert build_readme.safe_url("https://x.com/j(1)|x") == "https://x.com/j%281%29%7Cx"


def test_paginate_reports_cap():
    pages = lambda off: ([1] * 100, 5000)
    items, complete = adapters.paginate(pages, 100, cap=300)
    assert len(items) == 300 and complete is False


def test_us_cities_named_like_foreign_ones():
    for loc in ("Athens, GA", "Dublin, CA", "Paris, TX", "London, KY", "Vienna, VA, United States"):
        assert classify.us_job(loc), loc


def test_no_cpt_tag():
    assert classify.tags("We do not accept CPT or OPT for this role.")[0]["no_cpt"] is True
    assert classify.tags("This role is not eligible for OPT.")[0]["no_cpt"] is True
    assert classify.tags("We will not sponsor H-1B visas.")[0]["no_cpt"] is None


def test_final_audit_rows():
    for t in ("Electronic Security Intern", "2027 Intern - QA, QMS", "Tax & Data Analytics Intern",
              "Data Center Electrical Engineering Intern", "Undergraduate Financial Analytics Intern",
              "Silicon Photonics Packaging Engineer Co-op", "Defense Science and Technology Graduate Student Internship"):
        assert not classify.keep_title(t), t
    for t in ("QA Automation Intern", "Cybersecurity Risk Analyst Intern", "Electrical and Computer Engineering Intern"):
        assert classify.keep_title(t), t
    for loc in ("Zaragoza, ESP", "BRA", "Ovar, PT", "Wuxi, Jiangsu"):
        assert not classify.us_job(loc), loc


def test_expired_terms():
    nov = date(2026, 11, 9)
    assert classify.expired_term("2026 Summer Intern", nov) and classify.expired_term("Software Intern - Fall 2026", nov)
    assert classify.expired_term("2025 Co-op", nov)
    assert not classify.expired_term("Summer 2027 Software Engineering Intern", nov)
    assert not classify.expired_term("Software Engineering Co-op (Jan-Aug 2027)", nov)


def test_clearance_wording():
    t = classify.tags
    assert t("Upon start, you will be sponsored for a TS/SCI clearance.")[0]["sponsor"] is None
    assert t("A security clearance is not required for this role.")[0]["clearance"] is None
    assert t("This position is not eligible for sponsorship, OPT, or CPT.")[0]["no_cpt"] is True


def test_city_region_country_code_locations():
    # "City, Region, CC" (SmartRecruiters style): the last code is a country, even when it looks like a state
    assert not classify.us_job("Sofia, Bosch Digital, Sofia City Province, BG")
    assert not classify.us_job("Bengaluru, KA, IN")
    assert not classify.us_job("Toronto, ON, CA")
    assert classify.us_job("Austin, TX, US")
    assert classify.us_job("Indianapolis, Marion County, IN")
    assert classify.us_job("Dublin, CA") and classify.us_job("Athens, GA")


class _Resp:
    def __init__(self, code, text="", json_data=None):
        self.status_code, self.text, self.headers, self.ok, self._json = code, text, {}, code < 400, json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_http_stops_on_403_and_never_retries(monkeypatch):
    import common
    calls = []
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h, "robots_allow", lambda u: True)
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: calls.append(u) or _Resp(403))
    with pytest.raises(common.Blocked):  # a robots-checked site saying no is a block
        h.get("https://blocked.example/jobs")
    assert len(calls) == 1


def test_403_from_public_api_fails_today_but_is_not_a_permanent_block(monkeypatch):
    import common
    calls = []
    h = common.Http(gap=0)
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: calls.append(u) or _Resp(403))
    with pytest.raises(common.Unavailable):
        h.get("https://boards-api.greenhouse.io/v1/boards/acme/jobs")
    assert len(calls) == 1 and not issubclass(common.Unavailable, common.Blocked)


def test_timeouts_and_502_are_retried(monkeypatch):
    import common
    import requests
    seq = [requests.Timeout("slow"), _Resp(502), _Resp(200)]
    h = common.Http(gap=0)
    monkeypatch.setattr(common.time, "sleep", lambda s: None)

    def req(m, u, **k):
        x = seq.pop(0)
        if isinstance(x, Exception):
            raise x
        return x
    monkeypatch.setattr(h.s, "request", req)
    assert h.get("https://x.example/jobs").status_code == 200 and not seq


def test_unreachable_robots_txt_skips_today_without_blocking(monkeypatch):
    import common
    import requests
    monkeypatch.setattr(common, "_ROBOTS", {})
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h.s, "get", lambda u, **k: _Resp(503))
    with pytest.raises(common.Unavailable):
        h.get("https://down.example/api/jobs")
    monkeypatch.setattr(common, "_ROBOTS", {})
    def boom(u, **k):
        raise requests.ConnectionError("no route")
    monkeypatch.setattr(h.s, "get", boom)
    with pytest.raises(common.Unavailable):
        h.get("https://down2.example/api/jobs")


def test_url_key_keeps_job_id_params_that_look_like_tracking():
    import common
    assert common.url_key("https://x.com/job?refNo=123") != common.url_key("https://x.com/job?refNo=456")
    assert common.url_key("https://x.com/job?sourceId=9") != common.url_key("https://x.com/job")
    assert common.url_key("https://x.com/job?gh_jid=5&utm_source=li&source=x&ref=y") == common.url_key("https://x.com/job?gh_jid=5")


def test_failing_board_ages_out_instead_of_staying_open(tmp_path, monkeypatch):
    """One board out of four keeps failing (under the 30% abort): its rows go ⚠ and check_links removes them after 7 days."""
    comp = tmp_path / "companies.yaml"
    comp.write_text("companies:\n" + "".join(f"  - {{name: C{i}, ats: greenhouse, board: b{i}}}\n" for i in range(4)))
    for name, path in (("COMPANIES", comp), ("POSTINGS", tmp_path / "postings.json"), ("REMOVED", tmp_path / "removed.json"),
                       ("BLOCKED", tmp_path / "blocked.json")):
        monkeypatch.setattr(fetch_ats, name, path)
    broken = set()

    def fake(b, http):
        if b in broken:
            raise adapters.ShapeError("greenhouse: no jobs list")
        return adapters.Jobs([{"title": f"Software Engineering Intern {b}", "url": f"https://x.com/{b}", "location": "Austin, TX", "text": ""}])
    monkeypatch.setitem(adapters.CLOUD, "greenhouse", fake)
    monkeypatch.setattr(sys, "argv", ["fetch_ats.py", "--cloud"])
    monkeypatch.setattr(fetch_ats, "today", lambda: "2026-11-01")
    fetch_ats.main()
    broken.add("b3")
    for day in ("2026-11-02", "2026-11-05"):
        monkeypatch.setattr(fetch_ats, "today", lambda d=day: d)
        fetch_ats.main()
    rows = {r["company"]: r for r in json.loads((tmp_path / "postings.json").read_text())}
    assert rows["C3"]["status"] == "uncertain" and rows["C3"]["uncertain_since"] == "2026-11-02"
    assert all(rows[c]["status"] == "open" for c in ("C0", "C1", "C2"))
    monkeypatch.setattr(check_links, "POSTINGS", tmp_path / "postings.json")
    monkeypatch.setattr(check_links, "REMOVED", tmp_path / "removed.json")
    monkeypatch.setattr(check_links, "today_date", lambda: date(2026, 11, 10))
    monkeypatch.setattr(sys, "argv", ["check_links.py", "--stale-only"])
    check_links.main()
    left = {r["company"] for r in json.loads((tmp_path / "postings.json").read_text())}
    assert left == {"C0", "C1", "C2"}


def test_one_malformed_posting_does_not_fail_the_board():
    class H:
        def get(self, url, **k):
            return _Resp(200, json_data={"jobs": [{"title": "Software Engineering Intern", "absolute_url": "https://x.com/1"},
                                                  {"title": "broken, no url"}]})
    out = adapters.greenhouse("acme", H())
    assert [j["url"] for j in out] == ["https://x.com/1"]


def test_old_blocks_expire(board, tmp_path):
    state, run = board
    (tmp_path / "blocked.json").write_text(json.dumps({"greenhouse|acme": {"name": "Acme", "reason": "HTTP 403", "since": "2026-09-01"}}))
    rows = run("2026-11-01")  # 61 days later: asked again
    assert rows and all(r["status"] == "open" for r in rows.values())
    assert json.loads((tmp_path / "blocked.json").read_text()) == {}


def test_http_follows_robots_txt_when_asked(monkeypatch):
    import common
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h.s, "get", lambda u, **k: _Resp(200, "User-agent: *\nDisallow: /api/\n"))
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: _Resp(200))
    with pytest.raises(common.Blocked):
        h.get("https://robots.example/api/jobs")
    assert h.get("https://robots.example/careers").status_code == 200
    # documented APIs (Greenhouse, Lever...) don't check robots.txt
    plain = common.Http(gap=0)
    monkeypatch.setattr(plain.s, "request", lambda m, u, **k: _Resp(200))
    assert plain.get("https://robots.example/api/jobs").status_code == 200


def test_missing_robots_txt_means_allowed(monkeypatch):
    import common
    h = common.Http(gap=0, check_robots=True)
    monkeypatch.setattr(h.s, "get", lambda u, **k: _Resp(404))
    monkeypatch.setattr(h.s, "request", lambda m, u, **k: _Resp(200))
    assert h.get("https://norobots.example/api/jobs").status_code == 200


def _row(title, **tags):
    return {"company": "Acme", "title": title, "url": "https://x.com/1", "section": "internship", "tags": tags,
            "first_seen": date.today().isoformat(), "status": "open"}


def test_tag_str_shows_new_tags():
    s = build_readme.tag_str(_row("Software Intern - Fall 2027 Co-op", oa=True, min_gpa=3.0, clearance=True, clearance_level="secret"))
    for want in ("🧪 OA", "🎓 3.0+ GPA", "🔒 secret", "🔄 co-op", "🍂 fall"):
        assert want in s
    assert "🌱 spring" in build_readme.tag_str(_row("Spring Data Intern")) and "⏱ part-time" in build_readme.tag_str(_row("Part-Time IT Intern"))
    assert "🔒 clearance" in build_readme.tag_str(_row("Intern", clearance=True))  # no level stated


def test_clearance_level_filled_from_stored_evidence():
    r = _row("Intern", clearance=True)
    r["tag_evidence"] = {"clearance": "Active Top Secret clearance required."}
    assert "🔒 top secret" in build_readme.tag_str(r)


def test_track_rows_and_gov_overlap():
    rows = [_row("Firmware Intern"), _row("Software Intern", clearance=True), _row("Cybersecurity Intern")]
    assert [r["title"] for r in build_readme.track_rows(rows, "embedded")] == ["Firmware Intern"]
    assert [r["title"] for r in build_readme.track_rows(rows, "gov")] == ["Software Intern"]
    assert len(build_readme.track_rows(rows, "software")) == 1  # a gov row also stays on its main track


def test_manual_notes_never_become_public_tags(tmp_path, monkeypatch):
    import load_manual
    man, p = tmp_path / "m.yaml", tmp_path / "p.json"
    man.write_text('postings:\n  - {company: X, title: "Software Intern", url: "https://x.com/p", location: Remote,'
                   ' notes: "We are unable to sponsor visas. US citizens only."}\n')
    p.write_text("[]")
    monkeypatch.setattr(load_manual, "MANUAL", man)
    monkeypatch.setattr(load_manual, "POSTINGS", p)
    load_manual.main()
    r = json.loads(p.read_text())[0]
    assert not r["tags"].get("sponsor") and not r["tags"].get("citizen") and r["tags"].get("remote")
    assert "sponsor" not in r["tag_evidence"] and "citizen" not in r["tag_evidence"]


def test_laptop_closures_reach_removed_json(tmp_path, monkeypatch):
    from common import now_iso
    p, loc, rm = tmp_path / "p.json", tmp_path / "l.json", tmp_path / "r.json"
    p.write_text("[]")
    rm.write_text(json.dumps([{"id": "back", "removed_on": "2026-01-01"}, {"id": "old", "removed_on": "2026-01-01"}]))
    loc.write_text(json.dumps({"fetched_at": now_iso(),
                               "rows": [{"id": "back", "company": "X", "title": "t", "source": "workday"}],
                               "removed": [{"id": "gone", "removed_on": "2026-02-01"}, {"id": "old", "removed_on": "2026-01-01"}]}))
    for name, path in (("POSTINGS", p), ("LOCAL", loc), ("REMOVED", rm)):
        monkeypatch.setattr(merge_local, name, path)
    merge_local.main()
    ids = sorted(r["id"] for r in json.loads(rm.read_text()))
    assert ids == ["gone", "old"]  # new laptop closure added once, reopened row taken out, no duplicates


def test_validate_refuses_a_big_drop(tmp_path, monkeypatch):
    p = tmp_path / "p.json"
    p.write_text("[]")
    monkeypatch.setattr(validate, "POSTINGS", p)
    monkeypatch.setattr(validate, "previous_count", lambda: 100)
    with pytest.raises(SystemExit, match="refusing"):
        validate.main()


def test_validate_fails_in_ci_without_history(tmp_path, monkeypatch):
    p = tmp_path / "p.json"
    p.write_text("[]")
    monkeypatch.setattr(validate, "POSTINGS", p)
    monkeypatch.setattr(validate, "previous_count", lambda: None)
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(SystemExit):
        validate.main()
    monkeypatch.delenv("GITHUB_ACTIONS")
    validate.main()  # on a laptop it only warns


def test_check_links_open_resets_and_closed_twice_removes(tmp_path, monkeypatch):
    rows = [{"id": "a", "url": "https://a", "source": "manual", "status": "uncertain", "misses": 1, "uncertain_since": None},
            {"id": "b", "url": "https://b", "source": "manual", "status": "open", "misses": 1}]
    p, rm = tmp_path / "p.json", tmp_path / "r.json"
    p.write_text(json.dumps(rows))
    monkeypatch.setattr(check_links, "POSTINGS", p)
    monkeypatch.setattr(check_links, "REMOVED", rm)
    monkeypatch.setattr(check_links, "check", lambda http, url: "open" if url == "https://a" else "closed")
    monkeypatch.setattr(sys, "argv", ["check_links.py"])
    check_links.main()
    kept = json.loads(p.read_text())
    assert [r["id"] for r in kept] == ["a"] and kept[0]["misses"] == 0 and kept[0]["status"] == "open"
    assert [r["reason"] for r in json.loads(rm.read_text())] == ["link closed twice"]


def test_cells_escape_liquid_and_double_encoded_entities():
    out = build_readme.text("Intern {% include x %} {{ site.title }} {:.cls}")
    assert "{" not in out and "}" not in out
    assert build_readme.text("Data&amp;nbsp;Intern") == "Data Intern"
    assert build_readme.text("<script>alert(1)</script>") == "&lt;script&gt;alert\\(1\\)&lt;/script&gt;"


def test_must_have_matches_whole_company_names():
    k = build_readme.company_key
    assert k("Apple") != k("Apple Bank") and k("Intuit") != k("Intuitive Surgical") and k("Intel") != k("Inmar Intelligence")
    assert k("Intel") == k("Intel Corporation") and k("JPMorgan Chase") == k("JPMorgan Chase & Co.")
    assert k("AT&T") == "at and t" and k("Johnson & Johnson") == "johnson and johnson"
    assert k("Dell Technologies") == k("Dell Technologies Inc.") and k("Palantir") == k("Palantir Technologies")


def test_dedupe_prefers_open_copy_and_keeps_earliest_first_seen():
    import common
    a = {"id": "a", "company": "Acme", "title": "SWE Intern", "location": "Austin, TX", "status": "uncertain", "first_seen": "2026-11-01"}
    b = {"id": "b", "company": "ACME", "title": "SWE  Intern", "location": "austin, tx", "status": "open", "first_seen": "2026-11-05"}
    (r,) = common.dedupe_rows([a, b])
    assert r["id"] == "b" and r["first_seen"] == "2026-11-01"


def test_career_links_make_names_clickable():
    f = build_readme.career_links
    assert f(["Meta", "Acme"], {"Meta": "https://www.metacareers.com/"}) == "[Meta](https://www.metacareers.com/), Acme"
    assert f([], {"Meta": "https://www.metacareers.com/"}) == ""


def test_every_must_have_company_has_an_official_careers_page():
    must = build_readme.load_yaml(build_readme.DATA / "must_have.yaml", {})["companies"]
    pages = build_readme.load_yaml(build_readme.DATA / "career_pages.yaml", {})["pages"]
    assert [m for m in must if m not in pages] == []
    assert all(u.startswith("https://") and " " not in u for u in pages.values())


def test_manual_rows_expire_and_unverified_rows_show_the_warning(tmp_path, monkeypatch):
    import load_manual
    man, p = tmp_path / "m.yaml", tmp_path / "p.json"
    man.write_text('postings:\n'
                   '  - {company: A, title: "SWE Intern", url: "https://a.com/1", expires: "2026-11-10"}\n'
                   '  - {company: B, title: "SWE Intern", url: "https://b.com/1", expires: "2026-11-30", unverified: true}\n'
                   '  - {company: C, title: "SWE Intern", url: "https://c.com/1"}\n')
    p.write_text("[]")
    monkeypatch.setattr(load_manual, "MANUAL", man)
    monkeypatch.setattr(load_manual, "POSTINGS", p)
    monkeypatch.setattr(load_manual, "today_date", lambda: date(2026, 11, 16))
    load_manual.main()
    rows = {r["company"]: r for r in json.loads(p.read_text())}
    assert set(rows) == {"B", "C"}                                   # A expired and is gone
    assert rows["B"]["status"] == "uncertain" and rows["B"]["unverified"] and rows["B"]["uncertain_since"] is None
    assert rows["C"]["status"] == "open" and "unverified" not in rows["C"]
    man.write_text('postings:\n  - {company: B, title: "SWE Intern", url: "https://b.com/1", expires: "2026-11-30"}\n')
    load_manual.main()                                               # confirmed later: the warning goes away
    (r,) = json.loads(p.read_text())
    assert r["status"] == "open" and "unverified" not in r


def test_check_links_keeps_unverified_rows_marked_but_still_closes_dead_links(tmp_path, monkeypatch):
    rows = [{"id": "a", "url": "https://a", "source": "manual", "status": "uncertain", "unverified": True, "misses": 0, "uncertain_since": None},
            {"id": "b", "url": "https://b", "source": "manual", "status": "uncertain", "unverified": True, "misses": 0, "uncertain_since": None},
            {"id": "c", "url": "https://c", "source": "manual", "status": "uncertain", "unverified": True, "misses": 1, "uncertain_since": None}]
    p, rm = tmp_path / "p.json", tmp_path / "r.json"
    p.write_text(json.dumps(rows))
    monkeypatch.setattr(check_links, "POSTINGS", p)
    monkeypatch.setattr(check_links, "REMOVED", rm)
    states = {"https://a": "open", "https://b": "uncertain", "https://c": "closed"}
    monkeypatch.setattr(check_links, "check", lambda http, url: states[url])
    monkeypatch.setattr(sys, "argv", ["check_links.py"])
    check_links.main()
    kept = {r["id"]: r for r in json.loads(p.read_text())}
    assert set(kept) == {"a", "b"}                                   # c closed twice
    assert all(r["status"] == "uncertain" and r["uncertain_since"] is None for r in kept.values())  # no 7-day clock: expiry decides


def test_import_leads_page_states():
    import import_leads
    f = import_leads.page_state
    today = date(2026, 11, 16)
    page = "<html><h1>Software Engineer Intern, Maps &amp; Routing</h1> apply now</html>"
    assert f(200, page, "Software Engineer Intern, Maps & Routing", today) == "verified"
    assert f(200, "<html><div id=app></div></html>", "Software Engineer Intern", today) == "unverified"   # JavaScript shell
    assert f(404, "", "x", today) == "dead" and f(410, "", "x", today) == "dead"
    assert f(200, "This position has been filled. Software Engineer Intern", "Software Engineer Intern", today) == "unverified"
    assert f(200, '{"validThrough": "2026-11-01T00:00"} Software Engineer Intern', "Software Engineer Intern", today) == "dead"
    assert f(403, "", "x", today) == "unverified" and f(503, "", "x", today) == "unverified"


def test_import_leads_merge_extends_dedupes_and_drops_dead(tmp_path):
    import import_leads
    import yaml
    existing = [{"company": "Old", "title": "SWE Intern", "url": "https://o.com/1", "expires": "2026-11-20"},
                {"company": "Keep", "title": "SWE Intern", "url": "https://k.com/1", "expires": "2026-11-18"}]
    leads = [{"company": "Old", "title": "SWE Intern", "location": "Austin, TX", "url": "https://o.com/1", "state": "verified"},
             {"company": "New", "title": "Data Intern", "location": "Reston, VA", "url": "https://n.com/9", "state": "unverified"},
             {"company": "Gone", "title": "SWE Intern", "location": "", "url": "https://g.com/2", "state": "dead"}]
    out = import_leads.merge(existing, leads, date(2026, 11, 16), 14)
    by = {m["company"]: m for m in out}
    assert set(by) == {"Old", "Keep", "New"}
    assert by["Old"]["expires"] == "2026-11-30" and "unverified" not in by["Old"]      # a lead seen again gets 14 more days
    assert by["Keep"]["expires"] == "2026-11-18"                                       # not in this export: its own date stands
    assert by["New"]["unverified"] is True and by["New"]["expires"] == "2026-11-30"
    text = import_leads.render("# header\n", out)
    assert text.startswith("# header\npostings:\n") and yaml.safe_load(text)["postings"] == out


def test_import_leads_strips_invisible_characters_from_titles(tmp_path):
    import import_leads
    f = tmp_path / "l.csv"
    f.write_text("company,title,location,url\nAltice USA,Intern - DevOps Toolchain\u200b,\"Bethpage, NY\",https://x.com/1\n", encoding="utf-8")
    (lead,) = import_leads.read_leads(f)
    assert lead["title"] == "Intern - DevOps Toolchain"


def test_closed_wording_inside_page_code_does_not_close_a_job():
    import import_leads
    code = "<html><script>var msg = 'This job is no longer available';</script><!-- position has been filled --><body>Software Engineer Intern</body></html>"
    assert import_leads.page_state(200, code, "Software Engineer Intern", date(2026, 11, 16)) == "verified"
    shown = "<html><body><h1>Software Engineer Intern</h1><p>This job is no longer available</p></body></html>"
    assert import_leads.page_state(200, shown, "Software Engineer Intern", date(2026, 11, 16)) == "unverified"
    assert check_links.CLOSED_TEXT.search(check_links.visible(shown))
    assert not check_links.CLOSED_TEXT.search(check_links.visible(code))


def test_closed_wording_never_closes_a_link_on_its_own():
    class R:
        def __init__(self, code, text): self.status_code, self.text = code, text

    class H:
        def __init__(self, r): self.r = r
        def get(self, url, **kw): return self.r
    assert check_links.check(H(R(200, "<body>This job is no longer available</body>")), "u") == "uncertain"
    assert check_links.check(H(R(404, "")), "u") == "closed"
    assert check_links.check(H(R(200, "<body>Software Engineer Intern</body>")), "u") == "open"


def test_schema_accepts_the_unverified_flag_on_a_posting():
    import jsonschema
    schema = json.loads((validate.DATA / "schema.json").read_text(encoding="utf-8"))
    row = json.loads((validate.DATA / "postings.json").read_text(encoding="utf-8"))[0]
    row["unverified"] = True
    jsonschema.validate([row], schema, format_checker=jsonschema.FormatChecker())


def test_import_leads_upgrades_http_urls_to_https():
    import import_leads
    assert import_leads.https_url("http://prizepicks.com/position?gh_jid=1") == "https://prizepicks.com/position?gh_jid=1"
    assert import_leads.https_url("https://x.com/jobs/1") == "https://x.com/jobs/1"
    assert import_leads.https_url(" http://x.com/j ") == "https://x.com/j"


def test_paginate_caps_pages_at_the_row_limit():
    import build_readme
    pages = build_readme.paginate(list(range(300)), size=120)
    assert [len(p) for p in pages] == [120, 120, 60]
    assert build_readme.paginate([], size=120) == [[]]  # empty list still yields one page

def test_longest_first_orders_boards_by_last_known_size():
    import fetch_ats
    boards = [{"board": "a"}, {"board": "b"}, {"board": "c-new"}]
    rows = {1: {"board": "b"}, 2: {"board": "b"}, 3: {"board": "a"}}  # b=2, a=1, c-new=0 (no history)
    assert [c["board"] for c in fetch_ats.longest_first(boards, rows)] == ["b", "a", "c-new"]

def test_save_json_retries_when_the_file_is_briefly_locked(tmp_path, monkeypatch):
    import common
    p = tmp_path / "x.json"
    calls = {"n": 0}
    real = common.os.replace
    def flaky(src, dst):
        calls["n"] += 1
        if calls["n"] == 1:
            raise PermissionError("locked")
        return real(src, dst)
    monkeypatch.setattr(common.os, "replace", flaky)
    monkeypatch.setattr(common.time, "sleep", lambda s: None)
    common.save_json(p, {"a": 1})
    assert json.loads(p.read_text()) == {"a": 1}
    assert calls["n"] == 2  # failed once, then succeeded


def test_url_key_keeps_path_case_but_drops_tracking():
    from common import url_key
    assert url_key("https://Example.com/Job/ABC123/?utm_source=x") == "https://example.com/Job/ABC123"
    # two jobs whose links differ only in case are two jobs, not one
    assert url_key("https://e.com/J/ABC") != url_key("https://e.com/j/abc")
    assert url_key("https://e.com/j/1?gh_jid=7") == "https://e.com/j/1?gh_jid=7"  # a job id is kept


def test_rekey_rebuilds_ids_written_by_an_older_rule():
    """The guard against a url_key change making every posting look new: old ids are rebuilt on load,
    so first_seen survives and nothing is counted as closed."""
    stored = [{"id": "https://e.com/job/abc123", "url": "https://e.com/Job/ABC123", "first_seen": "2026-01-01"}]
    removed = [{"id": "https://e.com/job/old", "url": "https://e.com/Job/OLD"}]
    assert fetch_ats.rekey(stored, removed) == 2
    assert stored[0]["id"] == "https://e.com/Job/ABC123"
    assert stored[0]["first_seen"] == "2026-01-01"
    assert removed[0]["id"] == "https://e.com/Job/OLD"
    assert fetch_ats.rekey(stored, removed) == 0  # already current: nothing to do


def test_audit_sample_scores_a_clean_row_and_catches_an_unbacked_tag():
    """The accuracy audit has to fail a tag whose saved sentence no longer supports it."""
    import audit_sample
    clean = {"title": "Software Engineering Intern - Summer 2027", "location": "Austin, TX",
             "section": "internship", "url": "https://x.com/1", "company": "X",
             "tags": {"sponsor": False, "remote": False},
             "tag_evidence": {"sponsor": "We are unable to sponsor an employment visa."}}
    assert all(ok for ok, _ in audit_sample.audit_row(clean).values())

    unbacked = dict(clean, tags={"sponsor": False}, tag_evidence={"sponsor": "Great benefits and free lunch."})
    assert not audit_sample.audit_row(unbacked)["tag_backed"][0]

    nonus = dict(clean, location="London, United Kingdom")
    assert not audit_sample.audit_row(nonus)["us_location"][0]
