# Agent Atlas (Türkçe)

> AI agent'ın için açık web araştırma katmanı.

Bu dosya **Türkçe özet**. Ürün dili ve komutlar İngilizce kalır — ana doküman: [README.md](../README.md).

## Ne yapar?

Agent Atlas bir **yetenek katmanı**: kurar, sağlık kontrolü yapar, yönlendirir. Scraper değildir. Kurulumdan sonra agent doğrudan upstream CLI/API çağırır (Jina, Exa, yt-dlp, gh, twitter-cli, rdt-cli, OpenCLI, LinkedIn MCP).

**10 Batı kanalı.** Çin-only platformlar (Bilibili, Xiaohongshu…) kasıtlı olarak yok.

## Hızlı kurulum

Agent'a yapıştır:

```
Install Agent Atlas: https://raw.githubusercontent.com/batu3384/agent-atlas/main/docs/install.md
```

Manuel:

```bash
uv tool install agent-atlas-cli
# PyPI henüz yoksa:
uv tool install git+https://github.com/batu3384/agent-atlas.git

agent-atlas install
agent-atlas doctor
agent-atlas smoke
```

## Temel komutlar

| Komut | Anlamı |
|-------|--------|
| `agent-atlas doctor --json` | Kanal durumu + `active_backend` |
| `agent-atlas smoke` | Gerçek araştırma duman testi |
| `agent-atlas watch` | Hızlı sağlık + güncelleme ipucu |
| `agent-atlas check-update` | Yeni sürüm var mı? |

## Kanallar (özet)

| Tier | Kanallar |
|------|----------|
| 0 (login yok) | web (Jina), Exa, YouTube, GitHub, RSS |
| 1 (session) | Twitter, Reddit, LinkedIn (MCP→Jina), Facebook/Instagram (çoğu kurulumda kapalı) |

LinkedIn = Agent Reach modeli: `uvx linkedin-scraper-mcp@latest --login` + MCP.

## Dokümanlar

| Dosya | İçerik |
|-------|--------|
| [install.md](install.md) | Kurulum (agent + insan) |
| [tier1.md](tier1.md) | Login kanalları |
| [troubleshooting.md](troubleshooting.md) | Sık hatalar |
| [platforms.md](platforms.md) | Backend sırası |
| [update.md](update.md) | Güncelleme |

## Güvenlik

Cookie/token yerelde kalır. Twitter/Reddit/LinkedIn için **ikincil hesap** kullan.
