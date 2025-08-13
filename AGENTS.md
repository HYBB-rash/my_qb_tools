# Repository Guidelines

## Project Structure & Module Organization
- `src/`: Python package and CLIs
  - `tools/`: DB, services, qB API, move strategies (factory)
  - `share/`: logging, results, Telegram handler
  - `enqueue.py`, `execute.py`, `new_cfg.py`: CLI entry points
- `entry/`: PowerShell wrappers (`trigger.ps1`, `execute.ps1`)
- `test/`: Pytest suite (`test_*.py`)
- `cfg.json`: default configuration (category → library path)
- `data/`: SQLite DB (`app.db`, generated at runtime)
- `log/`: runtime logs (git-ignored)

## Build, Test, and Development Commands
- Create venv (Windows): `py -m venv .venv && .venv\\Scripts\\pip install -U pip`
- Install deps (simple): `pip install python-dotenv requests python-qbittorrent pytest`
- Or from project config: use your tool (uv/pdm/hatch/poetry) with `pyproject.toml`
- Run tests: `pytest -q`
- Enqueue: `python src/enqueue.py --name ... --category ... --tags "season=1,tmdb=243224-凡人修仙传" --content-path <path>`
- Execute next task: `python src/execute.py`
- Initialize cfg: `python src/new_cfg.py --season 1 --tmdb_id 243224 [--cfg '{...}']`

## Coding Style & Naming Conventions
- Python 3.12+, type hints preferred; keep functions small and explicit.
- Logging via `share.LOGGER`; messages are structured. Avoid print.
- UTF-8 for all source and file IO; Windows scripts may use UTF-8-BOM.
- Move strategy keys: `tmdb-<id>-s<season>` (e.g., `tmdb-243224-s1`).
- Linting/tools (optional): `ruff`, `mypy` available under dev deps.

## Testing Guidelines
- Framework: Pytest; tests live in `test/`, named `test_*.py`.
- Use temporary dirs and local SQLite (no network). Run with `pytest -q`.
- Add tests for new move strategies, DB operations, and logging behavior where feasible.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat(scope): ...`, `fix(scope): ...`, `chore(...): ...`.
- Include scope paths when meaningful (e.g., `entry/trigger`, `logging`, `move`).
- PRs should include: summary, rationale, screenshots/logs if relevant, and test coverage. Ensure `pytest -q` passes.

## Security & Configuration Tips
- Secrets from `.env`: `QBIT_URL`, `QBIT_USER`, `QBIT_PASSWORD`, `TMDB_API_TOKEN`, optional Telegram tokens.
- Do not commit `.env` or tokens. Configure logs via `MY_QB_TOOLS_LOG_FILE`; defaults to `log/app.log` (rotating, UTF-8).
- Hard links require same filesystem; handle cross-drive scenarios accordingly.
