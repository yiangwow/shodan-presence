"""Saved state (state.json) and the log file."""

import json
import os
import time
from datetime import datetime

from .config import LOG_FILE, STATE_FILE

try:
    with open(STATE_FILE, encoding="utf-8") as f:
        _state = json.load(f)
except Exception:
    _state = {}
_state.setdefault("spoken", 0)
_state.setdefault("played", {})  # iso date -> {exe: seconds}
_last_scan = {"t": time.time()}


def save_state():
    try:
        played = _state["played"]
        for day in sorted(played)[:-7]:  # keep a week
            del played[day]
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(_state, f)
    except Exception:
        pass


def log(line):
    """Append one diagnostic line; keep the tail bounded. Never raises."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%m-%d %H:%M:%S}  {line}\n")
        if os.path.getsize(LOG_FILE) > 200_000:
            with open(LOG_FILE, encoding="utf-8") as f:
                tail = f.readlines()[-800:]
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(tail)
    except Exception:
        pass
