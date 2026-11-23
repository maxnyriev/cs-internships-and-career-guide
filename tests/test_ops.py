"""The two scripts that guard operations: the staleness alarm and the robots.txt check.

Both were untested. A silent alarm is worse than no alarm, and a wrong robots URL means the
politeness check passes while asking about a path the board never reads.
"""
import json
from datetime import datetime, timedelta, timezone

import pytest

import check_freshness
import check_robots


def write_local(tmp_path, monkeypatch, payload):
    path = tmp_path / "local.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(check_freshness, "LOCAL", path)
    return path


def hours_ago(n, tz=True):
    t = datetime.now(timezone.utc) - timedelta(hours=n)
    return t.isoformat() if tz else t.replace(tzinfo=None).isoformat()


def test_fresh_laptop_data_passes(tmp_path, monkeypatch, capsys):
    write_local(tmp_path, monkeypatch, {"fetched_at": hours_ago(5), "rows": [{"id": "a"}]})
    check_freshness.main()
    assert "OK" in capsys.readouterr().out


def test_stale_laptop_data_fails_loudly(tmp_path, monkeypatch):
    write_local(tmp_path, monkeypatch, {"fetched_at": hours_ago(check_freshness.MAX_HOURS + 2), "rows": [{"id": "a"}]})
    with pytest.raises(SystemExit) as e:
        check_freshness.main()
    assert "::error::" in str(e.value) and "nightly.ps1" in str(e.value)


def test_one_missed_night_is_tolerated():
    """36 hours is deliberate: a single skipped run shouldn't page anyone."""
    assert 24 < check_freshness.MAX_HOURS < 48


def test_a_missing_file_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(check_freshness, "LOCAL", tmp_path / "nope.json")
    with pytest.raises(SystemExit) as e:
        check_freshness.main()
    assert "never pushed" in str(e.value)


@pytest.mark.parametrize("stamp", [None, "", "yesterday", 1763500000])
def test_an_unusable_timestamp_fails_with_a_readable_message(tmp_path, monkeypatch, stamp):
    """It used to raise KeyError or TypeError, so the alert arrived as a traceback."""
    write_local(tmp_path, monkeypatch, {"fetched_at": stamp, "rows": []} if stamp is not None else {"rows": []})
    with pytest.raises(SystemExit) as e:
        check_freshness.main()
    assert "fetched_at" in str(e.value)


def test_a_timestamp_without_a_zone_is_read_as_utc(tmp_path, monkeypatch, capsys):
    write_local(tmp_path, monkeypatch, {"fetched_at": hours_ago(2, tz=False), "rows": []})
    check_freshness.main()
    assert "OK" in capsys.readouterr().out


@pytest.mark.parametrize("company,expected", [
    ({"ats": "workday", "board": "3m.wd1/Search"},
     "https://3m.wd1.myworkdayjobs.com/wday/cxs/3m/Search/jobs"),
    ({"ats": "oracle", "board": "ehyf.fa.us2/CX_1"},
     "https://ehyf.fa.us2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions"),
    ({"ats": "amazon", "board": "-"}, "https://www.amazon.jobs/en/search.json"),
    ({"ats": "eightfold", "board": "careers.example.com|1234"},
     "https://careers.example.com/api/apply/v2/jobs"),
])
def test_robots_check_asks_about_the_url_the_board_actually_reads(company, expected):
    assert check_robots.api_url(company) == expected


def test_robots_check_has_no_url_for_an_unknown_source():
    """Sources outside ROBOTS_ATS are fetched without a robots lookup, so there's nothing to ask about."""
    assert check_robots.api_url({"ats": "greenhouse", "board": "x"}) is None
