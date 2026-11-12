# AGENTS.md

Project context, pipeline and music-theory rules are in `CLAUDE.md`; read it first.

- Tests: `python -m pytest -q` (Python 3.13, `pip install -r requirements.txt pytest`).
- Container: see the Container section in `CLAUDE.md`. The image runs as uid 1000 on a read-only root; write only to `DATA_DIR` or `/tmp`.
- Server headers (security headers, gzip, immutable static cache) live in `harden_and_compress` in `app.py`. Static URLs get `?v=<mtime>`; always link static files through `url_for('static', ...)`.
- Code, commits and PRs in English; the UI text is Dutch.
