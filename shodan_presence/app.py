"""The Discord session and the main loop."""

import random
import threading
import time
from datetime import datetime

from pypresence import Presence

from .config import CLIENT_ID, ROTATE_SECS
from .store import _state, log, save_state
from .lines.weird import distort
from .growth import maybe_grow
from .wall import watch_wall
from .cards import _arc, _card_key, _flags, _recent, pick_card, sanitize

def session():
    rpc = Presence(CLIENT_ID)
    rpc.connect()
    log("connected")
    while True:
        maybe_grow()
        card = pick_card()
        if not _flags["noguard"]:  # arcs/narration recur by design; rest re-rolls
            for _ in range(4):
                if _card_key(card) not in _recent:
                    break
                card = pick_card()
                if _flags["noguard"]:
                    break
        _recent.append(_card_key(card))
        rate = 0.12 if datetime.now().hour < 6 else 0.03
        if random.random() < rate:  # the wrongness injector
            field = random.choice(["details", "state"])
            if card.get(field):
                card[field] = distort(card[field])
        rpc.update(**sanitize(card))  # raises when the pipe dies (Discord closed)
        _state["spoken"] += 1
        save_state()
        log(f"push  {card.get('details', '')!r} / {card.get('state', '')!r}"
            f"  [arc queue: {len(_arc)}]")
        time.sleep(ROTATE_SECS)


def main():
    threading.Thread(target=watch_wall, daemon=True).start()

    while True:
        try:
            session()
        except Exception as exc:
            log(f"session ended: {type(exc).__name__}: {exc}")
            time.sleep(30)  # Discord not up yet / restarting — retry
