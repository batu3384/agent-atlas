# Agent Atlas — Plan

> Search and research the open web for your AI agent.

| | |
|---|---|
| **Ürün adı** | Agent Atlas |
| **Repo** | https://github.com/batu3384/agent-atlas |
| **Lisans** | MIT |
| **Dil** | İngilizce (ürün + docs) |
| **Durum** | v0.1.2 |
| **CLI** | Python (`agent-atlas`) |
| **Kapsam** | Western-only (10 kanal) |

---

## Tier 0 ✅
Web (Jina), Exa (mcporter), YouTube (yt-dlp), GitHub (gh), RSS (feedparser)

## Tier 1 ✅
| Kanal | Araç |
|---|---|
| Twitter | twitter-cli → OpenCLI |
| Reddit | rdt-cli → OpenCLI |
| LinkedIn | linkedin-mcp → Jina (Reach-style) |
| Facebook / Instagram | OpenCLI (`disabled_channels` sık) |

---

## Tamamlanan
- [x] Install / doctor / smoke / skill
- [x] Config → `apply_runtime_env`
- [x] rdt-cli; li-cli orphaned (not routed)
- [x] LinkedIn Reach parity (MCP → Jina; no OpenCLI/Chrome-open docs)
- [x] `watch` + `check-update`
- [x] CHANGELOG / SECURITY / CONTRIBUTING

## Bilinçli ertelenen
- [ ] **PyPI publish** — kurulum `uv tool` / `pipx` + git
- [ ] Çin platformları — out of scope
- [ ] i18n README
- [ ] Delete `li-cli/` package (optional cleanup)

---

*Son güncelleme: 2026-07-17 — v0.1.2*
