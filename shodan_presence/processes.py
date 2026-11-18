"""Finds running games and tools, and tracks play time."""

import os
import subprocess
import time
from datetime import datetime

from .config import NOWIN, SEEN_FILE, WIN
from .store import _last_scan, _state
from .lines.games import GAME_DIRS, HELPER_RE, REACTIVE

_first_seen = {}  # exe -> epoch when first observed running this session
try:
    with open(SEEN_FILE, encoding="utf-8") as f:
        _logged = set(f.read().splitlines())
except Exception:
    _logged = set()


def log_uncatalogued(unknown):
    """Remember uncatalogued games seen running, for later quote-writing."""
    new = unknown - _logged
    if new:
        _logged.update(new)
        try:
            with open(SEEN_FILE, "a", encoding="utf-8") as f:
                f.write("".join(e + "\n" for e in sorted(new)))
        except Exception:
            pass


def _exe_paths_windows():
    return subprocess.run(
        ["wmic", "process", "get", "ExecutablePath"], capture_output=True,
        text=True, timeout=20, **NOWIN,
    ).stdout.splitlines()


def _exe_paths_linux():
    """argv[0] of every process. Proton games show their Windows .exe path;
    native ones get ".exe" appended so REACTIVE keys match (factorio ->
    factorio.exe, wezterm-gui -> wezterm-gui.exe)."""
    paths = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                argv0 = f.read().split(b"\0", 1)[0].decode("utf-8", "replace")
        except OSError:
            continue
        if argv0 and not argv0.lower().endswith(".exe"):
            argv0 += ".exe"
        paths.append(argv0)
    return paths


def scan_processes():
    """Return (known, unknown): catalogued exe names running, and
    uncatalogued exe names running from a game directory."""
    known, unknown = set(), set()
    try:
        for path in (_exe_paths_windows() if WIN else _exe_paths_linux()):
            path = path.strip().lower().replace("/", "\\")
            if not path.endswith(".exe"):
                continue
            exe = path.rsplit("\\", 1)[-1]
            if exe == "javaw.exe" and "\\starsector\\" in path:
                exe = "starsector.exe"  # Starsector runs as its bundled java
            if exe in REACTIVE:
                known.add(exe)
            elif (path.startswith(GAME_DIRS) or "\\steamapps\\common\\" in path) \
                    and not HELPER_RE.search(exe):
                unknown.add(exe)
    except Exception:
        pass
    log_uncatalogued(unknown)
    elapsed = min(time.time() - _last_scan["t"], 300)  # cap gaps (sleep, arcs)
    _last_scan["t"] = time.time()
    today = _state["played"].setdefault(datetime.now().date().isoformat(), {})
    for exe in known | unknown:
        if exe not in ("wezterm-gui.exe", "obs64.exe", "spotify.exe", "wowvoiceproxy.exe"):
            today[exe] = today.get(exe, 0) + elapsed
    for exe in known:
        _first_seen.setdefault(exe, time.time())
    for exe in [e for e in _first_seen if e not in known]:
        del _first_seen[exe]
    return sorted(known), sorted(unknown)
