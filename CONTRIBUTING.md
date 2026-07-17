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

## Guidelines

1. Prefer small, focused PRs
2. Keep doctor/smoke honest — never report `ok` without a real probe
3. Update `docs/platforms.md` + skill `references/` when changing backend order
4. Add/adjust tests under `tests/`
5. English for product docs (`docs/README_tr.md` for Turkish summary); do not commit secrets

## Commit style

Short imperative subject; explain *why* in the body when non-obvious.

## Questions

Use GitHub Issues for bugs and feature requests.
