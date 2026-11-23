# Contributing

Anyone can help, whether or not you're at McNeese.

## Report a problem or suggest a company
Open a [GitHub issue](https://github.com/rohitpeets/cs-internships-and-career-guide/issues/new). Useful reports:
- A posting that's missing, dead, or mis-tagged (link it).
- A company we should add — ideally with the link to its job board (Greenhouse, Lever, Ashby, SmartRecruiters, Workday, Oracle, or Eightfold).

## Run it locally
Job sites aren't reachable from CI sandboxes, so fetching is run by a maintainer. Everything else runs anywhere:

```
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # Linux/macOS: .venv/bin/pip
.venv/Scripts/python -m pytest -q               # tests
.venv/Scripts/python scripts/build_readme.py    # rebuild the README and list pages
```

## How it's laid out
- `data/companies.yaml` — the list of company job boards that get fetched.
- `data/manual.yaml` — hand-added postings (verified/unverified, with expiry).
- `data/schema.json` — the schema every published posting must pass.
- `README.md`, `INTERNSHIPS.md`, `NEW_GRAD.md`, `EARLY.md`, `track-*.md` are **generated** by `scripts/build_readme.py` — don't edit them by hand.
- How the pipeline works: [docs/WRITEUP.md](docs/WRITEUP.md). Maintainer runbook: [docs/MAINTAINING.md](docs/MAINTAINING.md).

## Tests
Any change to the filter or tag rules in `scripts/classify.py` needs a test for the case, and all tests must pass (`pytest -q`).
