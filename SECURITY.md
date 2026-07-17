# Security Policy

## What Agent Atlas stores

| Data | Location | Permissions |
|------|----------|-------------|
| Atlas config | `~/.agent-atlas/config.yaml` | mode 600 |
| twitter-cli / OpenCLI env | process env from config | not written to disk by Atlas beyond config |
| rdt-cli credentials | `~/.config/rdt-cli/` | owned by rdt-cli (typically 600) |
| LinkedIn MCP session | `~/.linkedin-mcp/` | owned by linkedin-scraper-mcp |

Credentials stay on your machine. Agent Atlas does **not** upload cookies or tokens.

## Secondary accounts

Use **secondary** accounts for Twitter, Reddit, LinkedIn, Facebook, and Instagram. Automated / non-browser access can trigger platform bans.

## Reporting a vulnerability

Open a [GitHub issue](https://github.com/batu3384/agent-atlas/issues) with label `security`, or email the maintainer via the GitHub profile. Do not post live cookies or tokens in public issues.

## Safe install

```bash
agent-atlas install --safe      # list needs only
agent-atlas install --dry-run  # preview
```

## Scope

Agent Atlas is an installer/router. Upstream tools (OpenCLI, twitter-cli, yt-dlp, …) have their own security properties — review those projects separately.
