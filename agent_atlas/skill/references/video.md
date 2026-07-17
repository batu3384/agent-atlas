# Video — YouTube

## Capabilities
- Subtitles / auto-captions; title search via yt-dlp

## Prerequisites
- `yt-dlp` on PATH (`agent-atlas install`)

## Doctor
- `youtube` → `ok` when yt-dlp present

## Commands

```bash
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
yt-dlp --flat-playlist --print "%(title)s" "ytsearch5:query"
```

## Retry
1. Missing yt-dlp → install
2. No subs → `--write-auto-sub`; some videos have none

## Fallback
Tell the user — do not invent transcripts.

## Safety
Skip-download by default; write under `/tmp/`.
