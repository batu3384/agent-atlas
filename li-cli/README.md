# li-cli (experimental)

LinkedIn cookie sync + headless Chromium. **Often blocked by LinkedIn bot protection.**

For reliable LinkedIn research use **OpenCLI** (Chrome open + bridge):

```bash
opencli linkedin people-search "github" -f yaml
```

## Optional install

```bash
uv tool install -e ./li-cli
uv tool run --from playwright playwright install chromium
```

```bash
# Atlas Chrome closed after a real linkedin.com login in Profile 3
li login --force
li people-search "github" -n 5 --yaml
```

Credentials: `~/.config/li-cli/credential.json` (mode 600).

## Agent Atlas

Doctor prefers **OpenCLI → li-cli → Jina** for LinkedIn.
