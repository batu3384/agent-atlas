# Update Agent Atlas

Tell your agent:

```
Update Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/update.md
```

## Commands

```bash
# PyPI / uv tool
uv tool upgrade agent-atlas
# or
pipx upgrade agent-atlas
pip install -U agent-atlas

# Git fallback
uv tool install --force git+https://github.com/batu3384/agent-atlas.git
pipx install --force git+https://github.com/batu3384/agent-atlas.git

# Editable clone
cd /path/to/agent-atlas
git pull
pip install -e .
agent-atlas skill --install

agent-atlas doctor
agent-atlas check-update
agent-atlas smoke
```

## What to verify

```bash
agent-atlas doctor --json   # each channel active_backend
agent-atlas watch           # health + newer-version hint
```

Stuck? See [troubleshooting.md](troubleshooting.md).
