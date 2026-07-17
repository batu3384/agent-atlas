# Video — YouTube

## Transcripts / subtitles

```bash
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"
```

## Search (titles only)

```bash
yt-dlp --flat-playlist --print "%(title)s" "ytsearch5:query"
```

## Retry

1. `yt-dlp` missing → `pip install yt-dlp` or `agent-atlas install`
2. No subs → try `--write-auto-sub`; some videos have none
3. Geo/age blocks → tell the user; do not invent captions
