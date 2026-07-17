# Update Agent Atlas

Tell your agent:

```
Update Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/update.md
```

## Commands

```bash
# If installed via git clone + editable pip
cd /path/to/agent-atlas
git pull
pip install -e .
agent-atlas skill --install

# If installed via uv tool
uv tool upgrade agent-atlas
# or reinstall:
uv tool install --force git+https://github.com/batu3384/agent-atlas.git

# If installed via pipx
pipx upgrade agent-atlas
# or:
pipx install --force git+https://github.com/batu3384/agent-atlas.git

agent-atlas doctor
agent-atlas check-update
agent-atlas smoke
```

## What to verify

```bash
agent-atlas doctor --json   # each channel active_backend
agent-atlas watch           # health + newer-version hint
```
