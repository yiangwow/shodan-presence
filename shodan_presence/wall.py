"""The wall: shows her card fullscreen while she holds the living-room screen."""

import json
import time

from .config import WALL_ASSET, WALL_NOW
from .store import log

_wall = {"token": None, "until": 0.0}


def _monitors():
    """[(x, y, w, h)] of EVERY monitor. USER wants her on both screens
    (2026-09-30); measured layout then: primary 2560x1440 at 0,0 and a
    1920x1080 at 2560,150."""
    import ctypes
    import ctypes.wintypes as wt
    import struct
    ctypes.windll.user32.SetProcessDPIAware()  # Tk coords must be physical pixels
    found = []

    def cb(hmon, _dc, _rect, _data):
        info = ctypes.create_string_buffer(40)
        struct.pack_into("I", info, 0, 40)
        ctypes.windll.user32.GetMonitorInfoA(hmon, info)
        l, t, r, b = struct.unpack("I4i4iI", info.raw)[1:5]
        found.append((l, t, r - l, b - t))
        return 1

    proc = ctypes.WINFUNCTYPE(ctypes.c_int, wt.HMONITOR, wt.HDC, ctypes.POINTER(wt.RECT), wt.LPARAM)
    ctypes.windll.user32.EnumDisplayMonitors(0, 0, proc(cb), 0)
    return found


def _overlay(png, seconds):
    """Her card, fullscreen on EVERY monitor and on top of everything, for the
    rest of her minute. Esc dismisses it: an escape hatch, not an invitation."""
    import io
    import tkinter as tk
    from PIL import Image, ImageTk

    try:
        screens = _monitors()
    except Exception:
        screens = []
    root = tk.Tk()
    root.withdraw()
    if not screens:
        screens = [(0, 0, root.winfo_screenwidth(), root.winfo_screenheight())]
    card = Image.open(io.BytesIO(png)).convert("RGB")
    keep = []  # PhotoImages must outlive the mainloop
    for x, y, w, h in screens:
        win = tk.Toplevel(root)
        win.configure(bg="black", cursor="none")
        win.overrideredirect(True)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.attributes("-topmost", True)
        img = card.copy()
        img.thumbnail((w, h))
        photo = ImageTk.PhotoImage(img)
        keep.append(photo)
        tk.Label(win, image=photo, bg="black", bd=0).place(relx=0.5, rely=0.5, anchor="center")
        win.bind("<Escape>", lambda _e: root.destroy())
        win.focus_force()
    root.after(int(max(1.0, seconds) * 1000), root.destroy)
    root.mainloop()


def watch_wall():
    """Poll the living-room screen's 'now' marker; when she appears there,
    appear here too. Runs forever in a daemon thread; never raises."""
    import urllib.request
    while True:
        try:
            with urllib.request.urlopen(WALL_NOW, timeout=4) as r:
                body = r.read() if r.status == 200 else b""
            now = json.loads(body) if body else None
            if now and now.get("token") != _wall["token"] and now.get("until", 0) > time.time():
                _wall.update(token=now["token"], until=float(now["until"]))
                log(f"wall: she appeared ({now['token'][:8]})")
                with urllib.request.urlopen(WALL_ASSET.format(token=now["token"]), timeout=8) as r:
                    png = r.read()
                _overlay(png, _wall["until"] - time.time())
        except Exception:
            pass  # server down, endpoint absent, no display: try again shortly
        time.sleep(4)
