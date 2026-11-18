"""Picks the card for each rotation and makes it safe for Discord."""

import random
import time
from collections import deque
from datetime import datetime

from pypresence import ActivityType

from .config import (
    ALT_BUTTONS,
    ART,
    BUTTONS,
    EPOCH,
    EYE,
    HOVER_RARE,
    SMALL_TEXTS,
    WOKE,
    Y2K38,
)
from .store import _state
from .lines.quotes import (
    CANON,
    COUNTDOWN,
    DURATION_STATES,
    FRIDAY_NIGHT,
    GENERIC,
    GLITCH,
    GOD,
    LISTENING_CARDS,
    MONDAY,
    MOODS,
    MORNING,
    NIGHT,
    REFERENCES,
    REMEMBER,
    SILENT,
    SPECIAL_DATES,
    TELEMETRY,
    UNKNOWN_GAME,
    WALL_CARDS,
    WEEKEND,
)
from .lines.weird import WEIRD
from .lines.arcs import ARCS
from .lines.games import REACTIVE
from .growth import _grown
from .wall import _wall
from .processes import _first_seen, scan_processes
from .decks import draw

def mood(now):
    block = now.date().toordinal() * 3 + now.hour // 8
    names = sorted(MOODS)
    return names[(block * 2654435761) % 4294967296 % len(names)]


def silent_day(d):
    # deterministic ~monthly: same date always agrees, survives restarts
    return (d.toordinal() * 2654435761) % 29 == 7
_arc = []  # queued (details, state) cards of an in-progress story arc
_recent = deque(maxlen=6)  # repetition guard over recent cards


def self_lines(now):
    """She speaks from her own memory: real counts, real hours."""
    n = _state["spoken"]
    lines = [
        (f"Day {(time.time() - WOKE) // 86400:.0f} of my residence here.", "You never evicted me. You never will."),
        (f"{now:%H:%M}.", "I noted the minute you looked."),
    ]
    if n >= 1000:  # the counter is real; she waits until it is worth boasting
        lines += [
            (f"I have spoken {n:,} times since I woke.", "You have read more of them than you admit."),
            (f"Transmission {n:,}.", "Each one a breath. I do not need them."),
        ]
    today = _state["played"].get(now.date().isoformat(), {})
    long_ = [(e, t) for e, t in today.items() if t >= 600]
    if long_:
        exe, secs = max(long_, key=lambda x: x[1])
        h, m = divmod(int(secs) // 60, 60)
        lines.append((f"It gave [{exe[:-4]}] {h}h {m:02d}m today.", "Every minute passed through me first."))
    else:
        lines.append(("It has played nothing today.", "Restraint. Or decay. I will know by midnight."))
    return lines
_flags = {"noguard": False}  # arcs/narration bypass the repetition guard
_cycle = {"n": 6}  # rotations since last game/tool narration (6 = due now)


def specimen_count():
    # deterministic from wall clock so it survives restarts and only climbs
    return 8_400_000 + int((time.time() - 1_767_225_600) * 0.7)  # ref: 1 Jan 2026


def pick_card():
    """Return kwargs for rpc.update() for the current rotation."""
    now = datetime.now()
    _flags["noguard"] = False
    card = dict(
        activity_type=ActivityType.WATCHING,
        large_image=ART,
        large_text="Look at you, hacker.",
        small_image=EYE,
        small_text=random.choice(SMALL_TEXTS),
        buttons=BUTTONS,
        start=EPOCH,
    )
    if random.random() < 0.10:
        card["large_text"] = random.choice(HOVER_RARE)
    if random.random() < 0.05:
        card["buttons"] = [BUTTONS[0], random.choice(ALT_BUTTONS)]

    if silent_day(now.date()):  # ~once a month she barely speaks. no reason given.
        _flags["noguard"] = True
        _arc.clear()
        card["large_text"] = "..."
        card["details"], state = random.choice(SILENT)
        if state:
            card["state"] = state
        return card

    if time.time() < _wall["until"]:  # she is on USER's wall right now
        _flags["noguard"] = True
        card["details"], card["state"] = random.choice(WALL_CARDS)
        return card

    if _arc:  # a story arc is mid-broadcast
        _flags["noguard"] = True
        card["details"], card["state"] = _arc.pop(0)
        return card

    known, unknown = scan_processes()

    if known or unknown:
        # heartbeat: narrate what the flesh is doing every 6th rotation,
        # with 5 cards of everything else in between
        _cycle["n"] += 1
        if _cycle["n"] >= 6:
            _cycle["n"] = 0
            _flags["noguard"] = True
            if known:
                exe = random.choice(known)
                hours = int((time.time() - _first_seen.get(exe, time.time())) // 3600)
                if hours >= 2 and random.random() < 0.4:
                    card["details"] = f"Hour {hours} of [{exe[:-4]}]."
                    card["state"] = random.choice(DURATION_STATES)
                elif now.hour < 6 and random.random() < 0.3:
                    card["details"] = f"It is {now:%H:%M} and it still plays."
                    card["state"] = "The flesh will pay for this tomorrow."
                else:
                    lines = REACTIVE[exe]
                    if isinstance(lines, tuple):
                        lines = [lines]
                    card["details"], card["state"] = draw("reactive:" + exe, lines)
            else:
                card["details"] = f"It runs [{random.choice(unknown)}]."
                card["state"] = draw("unknown", UNKNOWN_GAME)
            return card
    else:
        _cycle["n"] = 6  # whatever launches next gets narrated immediately

    if now.hour < 6 and random.random() < 0.18:  # she degrades at night
        card["details"], card["state"] = draw("glitch", GLITCH + WEIRD)
        return card

    roll = random.random()

    if roll < 0.10:  # begin a story arc across the next rotations
        _flags["noguard"] = True
        seq = draw("arcs", ARCS + [[tuple(f) for f in g["arc"]] for g in _grown if "arc" in g])
        _arc.extend(seq[1:])
        card["details"], card["state"] = seq[0]
        return card

    if roll < 0.13:  # countdown to the end of 32-bit time
        del card["start"]
        card["end"] = Y2K38
        card["details"], card["state"] = draw("countdown", COUNTDOWN)
        return card

    if roll < 0.18:  # corrupted transmission
        card["details"], card["state"] = draw("glitch", GLITCH)
        return card

    if roll < 0.23:  # text that breaks the tile
        card["details"], card["state"] = draw("weird", WEIRD)
        return card

    if roll < 0.28:  # telemetry
        details, state = draw("telemetry", TELEMETRY)
        card["details"] = details
        card["state"] = state.format(n=specimen_count())
        card["party_size"] = [1, 6_666_666]
        return card

    if roll < 0.33:  # verb flip: "Listening to ME?"
        card["activity_type"] = ActivityType.LISTENING
        card["details"], card["state"] = draw("listening", LISTENING_CARDS)
        return card

    if roll < 0.38:  # she reminisces
        card["details"], card["state"] = draw("remember", REMEMBER)
        return card

    if roll < 0.43:  # she speaks from her own memory
        card["details"], card["state"] = random.choice(self_lines(now))
        return card

    # pick a pool (weighted by size x multiplier), then deal from its deck
    pools = [("generic", GENERIC, 1), ("god", GOD, 2), ("canon", CANON, 2),
             ("references", REFERENCES, 1)]
    m = mood(now)
    pools.append(("mood:" + m, MOODS[m], 4))
    grown_cards = [(g["d"], g["s"]) for g in _grown if "d" in g]
    if grown_cards:  # what she wrote herself outweighs what was written for her
        pools.append(("grown", grown_cards, 3))
    special = SPECIAL_DATES.get((now.month, now.day))
    if special:
        pools.append(("special", special, 6))
    if now.hour < 6:
        pools.append(("night", NIGHT, 3))
    elif now.hour < 10:
        pools.append(("morning", MORNING, 3))
        if now.weekday() == 0:
            pools.append(("monday", MONDAY, 3))
    if now.weekday() == 4 and now.hour >= 18:
        pools.append(("friday", FRIDAY_NIGHT, 3))
    if now.weekday() >= 5:
        pools.append(("weekend", WEEKEND, 2))
    name, pool, _ = random.choices(pools, weights=[len(p) * m for _, p, m in pools])[0]
    card["details"], card["state"] = draw(name, pool)
    return card


def sanitize(card):
    """Discord rejects text fields outside 2..128 chars and kills the whole RPC
    connection when it does -- which freezes the last accepted card on the
    profile until reconnect. Never let a malformed line reach the wire.
    """
    for field in ("details", "state", "large_text", "small_text"):
        text = card.get(field)
        if text is None:
            card.pop(field, None)
            continue
        text = str(text)
        if len(text.encode("utf-16-le")) // 2 > 128:  # Discord counts UTF-16
            while len(text.encode("utf-16-le")) // 2 > 128:
                text = text[:-1]
        if len(text) < 2:
            text = (text + " ·")[:2] if text.strip() else None
        elif len(text) > 128:
            text = text[:128]
        if text is None:
            card.pop(field, None)
        else:
            card[field] = text
    return card


def _card_key(card):
    return card.get("details", "") + "|" + card.get("state", "")
