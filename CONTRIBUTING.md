# Contributing

Thanks for helping improve Agent Atlas.

## Scope

- **In scope:** Western open-web research channels, installer/doctor/smoke, docs/SKILL
- **Out of scope by design:** China-only platforms (Bilibili, Xiaohongshu, …), write/post actions

## Dev setup

```bash
git clone https://github.com/batu3384/agent-atlas.git
cd agent-atlas
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Optional orphaned package (not routed by Atlas):

```bash
cd li-cli && uv sync && uv run pytest -q
```

## Guidelines

1. Prefer small, focused PRs
2. Keep doctor/smoke honest — never report `ok` without a real probe
3. Update `docs/platforms.md` + `SKILL.md` when changing backend order
4. Add/adjust tests under `tests/` for routing and parsers
5. English for product docs; do not commit secrets or cookie dumps

## Commit style

Short imperative subject; explain *why* in the body when non-obvious.

## Questions

Use GitHub Issues for bugs and feature requests.
