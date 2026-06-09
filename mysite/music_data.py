"""
Data and configuration for the interactive iPod music page (sect_ipod.html).

Keep this file focused on *content* (what to show) so the iPod UI in
static/js/ipod.js and the view logic in views.py stay generic. Adding a new
source later (e.g. "Music Recommendations") should mostly be a matter of adding
an entry here plus a small renderer in ipod.js.
"""

import json
from pathlib import Path

# --- YouTube -----------------------------------------------------------------
# Channel id for https://www.youtube.com/@DipenGupta (the "UC..." external id).
# Used to build the keyless Atom feed:
#   https://www.youtube.com/feeds/videos.xml?channel_id=<YOUTUBE_CHANNEL_ID>
YOUTUBE_CHANNEL_ID = "UC6Luaw5wf-XpJMPbbkxbTZw"

# The full back-catalogue (all uploads, newest first, with precise dates) lives
# in youtube_videos.json next to this file. The live RSS feed only returns the
# latest ~15, so the view merges any brand-new uploads on top of this archive.
# Refresh by asking Claude to re-scrape the channel.
_YOUTUBE_ARCHIVE_PATH = Path(__file__).resolve().parent / "youtube_videos.json"
try:
    YOUTUBE_VIDEOS = json.loads(_YOUTUBE_ARCHIVE_PATH.read_text(encoding="utf-8"))
except (OSError, ValueError):
    YOUTUBE_VIDEOS = []

# Shown if the live RSS fetch fails (network error, feed format change, etc.).
# Kept short on purpose; newest first (descending), mirroring the live feed.
# Each entry may also carry a "description" (the live feed provides real ones).
YOUTUBE_FALLBACK_VIDEOS = [
    {"videoId": "J-4-zvuavh0", "title": "Blues Jam at Champions Bar",
     "description": ""},
    {"videoId": "o5lLrQdkFfM",
     "title": "Green Day - Good Riddance (Time of Your Life) Cover",
     "description": ""},
    {"videoId": "_gKMKV816_8",
     "title": "Coke Studio - Afreen Afreen | Acoustic Guitar Cover",
     "description": ""},
    {"videoId": "-nHA7W6BdYk",
     "title": "Guns N' Roses - November Rain | Piano Cover",
     "description": ""},
    {"videoId": "e-41SapC6PU",
     "title": "John Mayer - In Your Atmosphere | Acoustic Guitar Cover",
     "description": ""},
]

# --- SoundCloud --------------------------------------------------------------
# The widget resolves this URL client-side and we read the track list straight
# from it via the Widget API (getSounds), so no server fetch / API key is
# needed. The page shows tracks in ascending order (oldest -> newest).
SOUNDCLOUD_USER_URL = "https://soundcloud.com/dipen-gupta/tracks"

# --- Instagram (UGG Chronicles) ----------------------------------------------
# Instagram exposes no keyless "list my reels" API and its embeds cannot play in
# the background, so this is a curated list rendered inline in the iPod screen.
# Add the reel "shortcode" (the bit after /reel/ in the URL), an optional
# "title" (shown in the menu list) and an optional "caption" (shown beneath the
# reel as a description). Example permalink:
#   https://www.instagram.com/reel/ABC123xyz/   ->   shortcode = "ABC123xyz"
#
# Newest first. Pulled from the public reels grid; refresh by asking Claude to
# re-scrape, or add new ones to the top by hand. The "UGG Chronicles" prefix is
# dropped from titles since the screen already shows it as the source label.
INSTAGRAM_REELS = [
    {"shortcode": "DY6RhBgNm1l", "title": "Ep. 214 | Radiohead - Fake Plastic Trees | Guitar Cover"},
    {"shortcode": "DYlU8ZUROUt", "title": "Ep. 213 | SOJA - Not Done Yet | Bass Cover"},
    {"shortcode": "DX-mAvWR-Bz", "title": "Ep. 212 | Green Day - Redundant | Guitar Cover"},
    {"shortcode": "DWz_KeFEUdb", "title": "Ep. 211 | Creedence Clearwater Revival - Have You Ever Seen The Rain | Bass Cover"},
    {"shortcode": "DVPxuDeES8C", "title": "Ep. 210 | G. Love & Special Sauce - Fatman | Guitar Cover"},
    {"shortcode": "DUW1a95kZp-", "title": "Ep. 209 | Elvis Presley - Jailhouse Rock | Guitar Cover"},
    {"shortcode": "DS7XnOXkYXA", "title": "Ep. 208 | Tere Bina | Guitar Cover"},
    {"shortcode": "DSGlBJzEfHn", "title": "Ep. 207 | Sleep Token - Gethsemane | Guitar Cover"},
    {"shortcode": "DRH9mCdkXTH", "title": "Ep. 206 | Wheatus - Teenage Dirtbag | Guitar Cover"},
    {"shortcode": "DQIitObkUHi", "title": "Ep. 205 | Audioslave - Cochise | Guitar Cover"},
    {"shortcode": "DOkGsQqESeR", "title": "Ep. 204 | Doubleneck Noodles"},
    {"shortcode": "DOEovApkeho", "title": "Ep. 203 | Kaisi Paheli Zindagani | Bass Cover"},
]

INSTAGRAM_PROFILE_URL = "https://www.instagram.com/dipengupta/reels/?hl=en"


def ipod_page_context():
    """Context for the iPod page that does not depend on a live network call.

    The live YouTube feed is fetched/cached in views.py (mirroring the tweet
    fetch); everything else is static config and is assembled here.
    """
    return {
        "soundcloud_user_url": SOUNDCLOUD_USER_URL,
        "instagram_reels": INSTAGRAM_REELS,
        "instagram_profile_url": INSTAGRAM_PROFILE_URL,
    }
