"""LinkedIn CLI constants."""

from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "li-cli"
CREDENTIAL_FILE = CONFIG_DIR / "credential.json"
BROWSER_PROFILE_DIR = CONFIG_DIR / "browser-profile"
CREDENTIAL_TTL_DAYS = 7

BASE_URL = "https://www.linkedin.com"
PEOPLE_SEARCH_URL = f"{BASE_URL}/search/results/people/"

REQUIRED_COOKIES = {"li_at"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    ),
    "sec-ch-ua": '"Chromium";v="133", "Not(A:Brand";v="99", "Google Chrome";v="133"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Accept-Language": "en-US,en;q=0.9",
}
