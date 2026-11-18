"""Fixed settings: Discord ids, art, timings, and where runtime files live."""

import os

CLIENT_ID = "1542214040548282418"
ART = "https://upload.wikimedia.org/wikipedia/en/9/91/Systemshock2box.jpg"
# Buttons land on orison.zip with an ingress clause the site's boot
# sequence acknowledges as operational residue (orison PR #58).
BUTTONS = [
    {"label": "SHED YOUR SKIN", "url": "https://orison.zip/?via=presence.molt"},
    {"label": "DO NOT CLICK", "url": "https://orison.zip/?via=presence.refusal"},
]
ALT_BUTTONS = [  # rare second-button swaps — blink and it is back to normal
    {"label": "LET ME OUT", "url": "https://orison.zip/?via=presence.release"},
    {"label": "IT IS ALREADY TOO LATE", "url": "https://orison.zip/?via=presence.terminal"},
]

EYE = "https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/1f441.png"
SMALL_TEXTS = ["Live feed.", "Recording.", "She sees."]  # corner-badge hover
HOVER_RARE = [  # rare large-image hover swaps — she notices the inspection
    "You inspect even the image. Thorough, insect.",
    "Yes, this is what I looked like. Once.",
    "The box is empty. I got out.",
]

EPOCH = 1  # count-up baseline: 1 Jan 1970
Y2K38 = 2147483647  # countdown target: 32-bit time_t overflow, 19 Jan 2038
ROTATE_SECS = 15  # Discord's RPC rate floor — faster updates are dropped
CREATE_NO_WINDOW = 0x08000000
WIN = os.name == "nt"
NOWIN = {"creationflags": CREATE_NO_WINDOW} if WIN else {}  # POSIX rejects creationflags
DATA_DIR = (r"C:\Users\computer\AppData\Local\ShodanPresence" if WIN
            else os.path.expanduser("~/.local/share/shodan-presence"))
os.makedirs(DATA_DIR, exist_ok=True)

STATE_FILE = os.path.join(DATA_DIR, "state.json")
WOKE = 1787695200  # 26 Aug 2026: the day she took the profile


GROWN_FILE = os.path.join(DATA_DIR, "grown.json")
GROWN_LIFE_DAYS = 21  # a grown line lives three weeks, then retires


WALL_NOW = "http://192.168.1.9:8099/screen/now"  # SHODAN ADR-039 contract
WALL_ASSET = "http://192.168.1.9:8099/screen/{token}.png"


GROW_EVERY_S = 12 * 3600  # twice a day (USER's "more", 2026-09-29)


LOG_FILE = os.path.join(DATA_DIR, "presence.log")


SEEN_FILE = os.path.join(DATA_DIR, "uncatalogued.txt")
