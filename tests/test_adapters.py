import json
from pathlib import Path

import pytest

import adapters

FIX = Path(__file__).parent / "fixtures"


class FakeResp:
    def __init__(self, data, status=200):
        self._d, self.status_code, self.ok = data, status, status < 400

    def json(self):
        return self._d

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeHttp:
    def __init__(self, data, status=200):
        self.r = FakeResp(data, status)

    def get(self, *a, **k):
        return self.r


@pytest.mark.parametrize("name", ["greenhouse", "lever", "ashby"])
def test_fixture_parses(name):
    data = json.loads((FIX / f"{name}.json").read_text(encoding="utf-8"))
    jobs = adapters.CLOUD[name]("demo", FakeHttp(data))
    assert jobs and all(j["title"] and j["url"].startswith("http") for j in jobs)


@pytest.mark.parametrize("name,bad", [("greenhouse", {"oops": 1}), ("lever", {"jobs": []}), ("ashby", [])])
def test_unexpected_shape_fails_loudly(name, bad):
    with pytest.raises(adapters.ShapeError):
        adapters.CLOUD[name]("demo", FakeHttp(bad))


def test_smartrecruiters_parses():
    class H:
        def get(self, url, params=None, **k):
            if params:  # list call
                data = {"content": [{"id": "1", "name": "Software Engineer Intern", "location": {"city": "Austin", "region": "TX", "country": "us"}}],
                        "totalFound": 1} if params["q"] == "intern" else {"content": [], "totalFound": 0}
            else:  # detail call
                data = {"postingUrl": "https://jobs.smartrecruiters.com/acme/1",
                        "jobAd": {"sections": {"qualifications": {"text": "<p>We are unable to sponsor visas.</p>"}}}}
            return FakeResp(data)
    jobs = adapters.CLOUD["smartrecruiters"]("acme", H())
    assert [j["location"] for j in jobs] == ["Austin, TX, US"] and "unable to sponsor" in jobs[0]["text"]


def test_amazon_parses():
    data = {"hits": 1, "jobs": [{"id": "1", "title": "2027 Software Dev Engineer Intern", "job_path": "/en/jobs/1/sde-intern",
                                 "normalized_location": "Seattle, Washington, USA", "description": "Build things.",
                                 "basic_qualifications": "Enrolled in a CS degree.", "preferred_qualifications": ""}]}
    jobs = adapters.CLOUD["amazon"]("amazon", FakeHttp(data))
    assert jobs[0]["url"] == "https://www.amazon.jobs/en/jobs/1/sde-intern" and "CS degree" in jobs[0]["text"]


def test_posted_date_formats():
    from common import today_date
    p = adapters.posted_date
    assert p("2026-07-21T19:49:28-04:00") == "2026-07-21"           # Greenhouse first_published, Ashby publishedAt
    assert p(1760000000000) == p(1760000000) == "2025-10-09"        # Lever ms, Eightfold seconds
    assert p("November 3, 2026") == "2026-11-03"                    # Amazon
    assert p("2099-01-01") == today_date().isoformat()              # never in the future
    assert p("garbage") is None and p(None) is None


class RouteHttp:
    """Answers by URL: list/search calls get `listing`, detail calls get `detail`."""
    def __init__(self, listing, detail, is_detail):
        self.listing, self.detail, self.is_detail = listing, detail, is_detail

    def get(self, url, **k):
        return FakeResp(self.detail if self.is_detail(url) else self.listing)

    def post(self, url, **k):
        return FakeResp(self.listing)


# Shapes follow the fields each parser reads. Replace with saved live responses when you next run with network.
def test_workday_parses_list_and_detail():
    listing = {"total": 1, "jobPostings": [{"title": "Software Engineering Intern", "externalPath": "/job/Austin-TX/SWE-Intern_R1",
                                            "locationsText": "Austin, TX"}]}
    detail = {"jobPostingInfo": {"externalUrl": "https://acme.wd1.myworkdayjobs.com/careers/job/R1", "location": "Austin, TX",
                                 "jobDescription": "<p>Must be a U.S. citizen.</p>", "startDate": "2026-10-01"}}
    jobs = adapters.LOCAL["workday"]("acme.wd1/careers", RouteHttp(listing, detail, lambda u: "/job/" in u))
    assert len(jobs) == 1 and jobs.complete
    j = jobs[0]
    assert j["url"].endswith("/job/R1") and j["location"] == "Austin, TX" and "U.S. citizen" in j["text"] and j["posted"] == "2026-10-01"


def test_oracle_parses_list_and_detail():
    listing = {"items": [{"TotalJobsCount": 1, "requisitionList": [{"Id": "123", "Title": "Software Developer Intern",
                                                                    "PrimaryLocation": "Houston, TX", "PostedDate": "2026-09-15"}]}]}
    detail = {"items": [{"ExternalDescriptionStr": "<p>Build tools.</p>", "ExternalQualificationsStr": "<li>CS major</li>"}]}
    jobs = adapters.LOCAL["oracle"]("acme.fa.us2/CX_1", RouteHttp(listing, detail, lambda u: "Details" in u))
    assert len(jobs) == 1
    j = jobs[0]
    assert j["url"].endswith("/sites/CX_1/job/123") and "CS major" in j["text"] and j["posted"] == "2026-09-15"


def test_eightfold_parses_list_and_detail():
    listing = {"count": 1, "positions": [{"id": 7, "name": "Software Engineer Intern", "location": "Los Gatos, CA",
                                          "canonicalPositionUrl": "https://explore.jobs.example.net/careers/job/7", "t_create": 1760000000}]}
    detail = {"job_description": "<p>Work on streaming.</p>"}
    jobs = adapters.CLOUD["eightfold"]("explore.jobs.example.net|example.com", RouteHttp(listing, detail, lambda u: u.endswith("/7")))
    assert len(jobs) == 1 and jobs[0]["text"] == "Work on streaming." and jobs[0]["posted"] == "2025-10-09"


@pytest.mark.parametrize("name,where", [("workday", "LOCAL"), ("oracle", "LOCAL"), ("eightfold", "CLOUD")])
def test_new_sources_fail_loudly_on_odd_shapes(name, where):
    board = {"workday": "acme.wd1/careers", "oracle": "acme.fa.us2/CX_1", "eightfold": "h.example.net|example.com"}[name]
    with pytest.raises(adapters.ShapeError):
        getattr(adapters, where)[name](board, RouteHttp({"oops": 1}, {}, lambda u: False))
