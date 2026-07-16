# Publishing to PyPI

Package builds with:

```bash
python -m build
```

## Trusted Publishing (preferred)

One-time on https://pypi.org/manage/account/publishing/ :

| Field | Value |
|-------|--------|
| PyPI project name | `agent-atlas` |
| Owner | `batu3384` |
| Repository | `agent-atlas` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Then either:

- Draft a GitHub Release → publish workflow uploads, or
- Actions → **Publish to PyPI** → Run workflow

## Token (manual)

```bash
export UV_PUBLISH_TOKEN=pypi-AgEIcHlwaS5vcmc...
uv publish
# or: twine upload dist/*
```
