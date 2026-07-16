# Agent Atlas — Plan

> Search and research the open web for your AI agent.

| | |
|---|---|
| **Ürün adı** | Agent Atlas |
| **Repo / klasör** | `agent-atlas` |
| **Konum** | `~/Documents/agent-atlas/` |
| **Lisans** | MIT |
| **Dil** | İngilizce (ürün + docs) |
| **Durum** | v0.1.0 — GitHub repo canlı |
| **CLI** | Python (`agent-atlas`) |
| **Web arama** | Exa + mcporter |

---

## Kapsam

### Tier 0 ✅
Web (Jina), Exa, YouTube, GitHub, RSS

### Tier 1 ✅ (araçlar kurulu; oturum kullanıcıda)
| Kanal | Araç |
|---|---|
| Twitter | twitter-cli (tercih) → OpenCLI |
| Reddit / FB / IG | OpenCLI + Chrome bridge |
| LinkedIn | OpenCLI adapter → Jina public |

Rehber: `docs/tier1.md`

---

## Yol haritası

### Faz 0–2
- [x] Plan, iskelet, Tier 0 canlı, sync SSOT

### Faz 3 — Tier 1
- [x] `docs/tier1.md` (OpenCLI, twitter-cli, güvenlik)
- [x] Doctor: OpenCLI bridge parse (FAIL → warn)
- [x] `install --channels opencli,twitter` (npm + uv tool)
- [x] SKILL / platforms / sync references

### Faz 4 — Repo
- [x] GitHub repo: https://github.com/batu3384/agent-atlas
- [x] llms.txt + release v0.1.0

### İyileştirme backlog
- [x] Config → runtime env (`apply_runtime_env` on CLI start)
- [x] Doctor hızı: tek `opencli doctor` + `list` cache
- [x] End-to-end research smoke (`agent-atlas smoke`)
- [x] GitHub repo (Faz 4)

---

## Kullanıcı adımları (Chrome)

1. OpenCLI Chrome extension kur  
2. İkincil hesaplarla sitelere login ol  
3. `opencli doctor` → connected  
4. `agent-atlas doctor` / `agent-atlas smoke`

**Not:** `twitter-cli` tarayıcı cookie’sini otomatik okuyabilir — ana hesap riski. Mümkünse ayrı profil / ikincil hesap kullan.

Config anahtarları (`twitter_chrome_profile`, `opencli_profile`, …) `agent-atlas` çalışınca otomatik env’e yazılır.

---

*Son güncelleme: 2026-07-16 — Faz 4: GitHub + smoke*
