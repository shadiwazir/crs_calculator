> **About this project:** this project is a proof of concept (PoC) for the **accuracy of AI-agent implementation**.
>
> - **Technique used for the agent instructions:** the implementing agent (Claude) was driven **solely by prompt engineering**, and the prompts/reviews steering it were produced by **meta-prompt engineering** (Gemini).
> - **Total duration:** ~30 minutes from start to end, including a quick smoke test.
> - **Manual check:** the UI was tested manually in a browser (it loads and the score changes with the inputs); no scores have been compared against the official calculator yet.
> - **Status of acceptance:** the real acceptance test is **still pending real-user feedback**. Treat results as unverified until they are compared with the official IRCC calculator.

# CRS Calculator

Express Entry Comprehensive Ranking System (CRS) calculator: a small Flask web app backed by a pure-Python scoring core. Scores out of 1,200 with a per-section breakdown.

- Rules, sources and the decisions taken: [REQUIREMENTS_ANALYSIS.md](REQUIREMENTS_ANALYSIS.md) (based on the IRCC [CRS criteria](https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html) page, "date modified 2026-06-22").
- Language input is **raw test scores** (CELPIP-General, IELTS General Training, PTE Core, TEF Canada, TCF Canada), converted to CLB/NCLC with IRCC's conversion tables.
- **No job-offer points**: they were removed from the CRS on 2025-03-25.
- Estimates only; the official Express Entry system's score governs.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/pytest             # run tests (308)
.venv/bin/python -m crs.web  # serve http://127.0.0.1:5000 (Flask dev server)
```

## Run with Docker

```bash
docker compose up -d --build        # http://localhost:8000 (override with PORT=...)
docker compose down
```

The image runs gunicorn on port 8000 as a non-root user.

Publish to Docker Hub (builds, tags `<version from pyproject.toml>` and `latest`, pushes; run `docker login` first):

```bash
DOCKERHUB_USER=<your-username> scripts/publish.sh [version]
```

## Layout

```
src/crs/
  tables.py           all point values, bands, caps and test-conversion grids (data only)
  engine.py           band lookup helper
  language_mapper.py  raw test score -> CLB/NCLC per ability (with validation)
  models.py           Profile / SpouseProfile, validation, marital-status resolution
  sections/           core.py, spouse.py, transferability.py, additional.py
  calculator.py       orchestration, caps, breakdown
  web/                Flask app (app.py, schema.py), templates/, static/
tests/                pytest, table-driven
scripts/publish.sh    build, tag and push the Docker image
```

## License

MIT – see [LICENSE](LICENSE).
