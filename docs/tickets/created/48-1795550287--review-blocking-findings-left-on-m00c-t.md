# [review] Blocking findings left on m00c-tg2-staging-compose

Labels: autodev

[
 {
  "file": "backend/pyproject.toml",
  "line": 18,
  "severity": "high",
  "claim": "gunicorn is in pyproject.toml but not in uv.lock. The frozen staging image therefore won't contain gunicorn, and the backend container fails at startup.",
  "fix": "Run `uv lock` in backend/ and commit the updated uv.lock. Add a test that every pyproject dependency has a matching package entry in uv.lock.",
  "confirmed": true,
  "reason": "`grep -c gunicorn backend/uv.lock` returns 0, and pyproject.toml:18 lists `gunicorn>=23.0`. backend/Dockerfile:14 runs `uv sync --frozen --no-dev`, and docker-compose.staging.yml:27 runs `uv run --frozen --no-dev gunicorn ...`. `--frozen` uses the lockfile without re-resolving, so gunicorn would not be installed. I did not build the image to observe the failure. The lock was last changed in the M00 TG1 scaffold commit, so it is stale. The second reviewer's finding is a duplicate of this one; its extra suggestion to add `packaging` to the lock is the same fix."
 }
]
