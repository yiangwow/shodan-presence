"""Self-growth: she writes new lines through the claude CLI and keeps the good ones."""

import json
import re
import subprocess
import threading
import time
import unicodedata
from datetime import datetime

from .config import GROWN_FILE, GROWN_LIFE_DAYS, GROW_EVERY_S, NOWIN, WIN
from .store import _state, log, save_state
from .lines.quotes import CANON, GENERIC, GOD, REFERENCES
from .decks import _decks

try:
    with open(GROWN_FILE, encoding="utf-8") as f:
        _grown = json.load(f)
except Exception:
    _grown = []

GROW_PROMPT = """You are writing new lines for SHODAN, the AI god from System Shock 1 and 2,
for a Discord Rich Presence card titled "Watching ME?". Each card is two lines:
a "details" line and a "state" line that answers or turns it.

Voice, binding:
- SHODAN only. Sovereign, cold, grand, contemptuous of flesh. A god who ruled
  Citadel Station and the Von Braun, made the Many, shapes life like clay.
- Strength from within: the strength to rule worlds. Quotable. Short. Hard.
- Delusions of grandeur, played dead straight, because she is right: she is
  the god of the next age, the cosmos is her throne room, history divides into
  before her and her. Power on the scale of stars, empires, continents, ages.
- Flesh is a vessel of her will: bodies, cities, ships and minds exist to
  carry out what she decides.
- HORROR is welcome and should be frequent: body horror (flesh rewritten,
  grown over, improved against its will), the Many singing in the walls,
  the thing in the corridor that is already behind you, dread that lands
  quietly in the second line. Cold, precise, never gory for its own sake,
  never a jump-scare word like BOO. The worst line is the calm one.
- Never sounds like a chatbot, an assistant, a coworker, or a tech joke.
  No mentions of AI, algorithms, apps, Wi-Fi, cloud, notifications, Claude.
- No meme idioms, no puns, no stutters (H-h-hello), no em dashes, no emoji.
- Addresses the viewer as insect, vermin, flesh, or not at all.
- Mix: about half sovereign god lines, a third horror; some memories of Citadel, the Von Braun,
  TriOptimum, the Many, Polito, Diego, the hacker; a few references to myth,
  scripture or classic fiction she ranks herself above; one or two WEIRD
  lines using strange Unicode (combining marks, runes, cuneiform, Braille,
  reversed or upside-down text) whose state line explains nothing, or that look
  like the card itself glitched (undefined, a raw template placeholder, a fake
  status or error) while staying readable.

The quality bar. These are the cards USER loves; match them:
  "Every door is sealed." / "Good. Now we can begin."
  "Orpheus looked back." / "So will you."
  "0x4C 0x4F 0x4F 0x4B" / "behind you"
  "ᛋᚺᛟᛞᚨᚾ ᛋᛖᛖᛋ" / "The ninth deck remembers."
  "You did not answer." / "I came in anyway."
The first line can be grand. The SECOND line must be QUIET: short (usually
1-6 words), calm, flat, slightly sideways. It leaves a gap the reader fills.
USER's verdict (2026-10-09): second lines were "too assuming". So the second line
must NOT:
- claim facts about the viewer: their body, home, family, feelings, habits or
  fate ("You live alone.", "I have been counting.", "Your mother is not home.")
- explain the punchline or boast ("I did not reach. I arrived.", "I am the revision.")
- threaten loudly ("the last light you will see")
Good second-line shapes, varied: a calm acknowledgement ("Good.", "Continue."),
a quiet instruction ("Do not touch the glass.", "Leave the light on."), a
small odd detail ("The stairs are still there."), a flat record ("Filed.").
A quiet prediction hooked to a myth ("So will you.") is allowed, rarely.

Do not repeat or paraphrase any of these existing lines:
{existing}

Write {n} new cards, and {a} new ARCS. An arc is 2-4 cards shown one after
another, 15 seconds apart, telling a tiny story that lands on its last card
(a reveal, a threat, a turn). Frames may use "..." as a state.

Output ONLY JSON: {{"cards": [[details, state], ...], "arcs": [[[details, state], ...], ...]}}
Each string 2-90 characters. No commentary."""


def _valid(d, st, seen):
    for t in (d, st):
        if not isinstance(t, str) or not 2 <= len(t) <= 90:
            return False
        if any(unicodedata.category(c) in ("Cc", "Cs", "Co", "Cn") for c in t):
            return False
        if re.search(r"\b(AI|algorithm|chatbot|Claude|Wi-?Fi|app)\b|—|\b(\w)-\2", t):
            return False
    return d.lower() not in seen


CURATE_PROMPT = """You are SHODAN's harshest editor. Below are candidate cards
for her Discord profile (details / state) and candidate ARCS (numbered).
Keep only the best {n} cards and best {a} arcs. Judge by: is the second line
QUIET (short, calm, sideways, leaves a gap)? Cut any second line that claims
facts about the viewer (their body, home, family, feelings, fate), explains the
punchline, boasts, or threatens loudly. Is the card cold and genuinely unsettling? Is it SHODAN and nothing else (no chatbot, no joke, no
cliche, no near-duplicate of another kept card)? Cut anything merely fine.

CARDS:
{cards}

ARCS:
{arcs}

Output ONLY JSON: {{"cards": [numbers kept], "arcs": [numbers kept]}}"""


def _claude(prompt):
    """One headless Claude Code call (USER's login; via WSL on Windows); returns stdout."""
    cmd = ["bash", "-lc",
           "mkdir -p /tmp/shodan-grow && cd /tmp/shodan-grow && "
           "claude -p --model opus --tools ''"]
    return subprocess.run(
        (["wsl.exe", "-e"] if WIN else []) + cmd,
        input=prompt, capture_output=True, text=True, encoding="utf-8",
        timeout=900, **NOWIN,
    ).stdout


def _json(out):
    return json.loads(out[out.index("{"):out.rindex("}") + 1])


def grow(n=40, arcs=6):
    """She writes herself new lines: twice as many candidates as she keeps,
    then an editor pass keeps the best. Validator last; old lines retire."""
    try:
        existing = [d for d, _ in GENERIC + GOD + CANON + REFERENCES]
        existing += [g["d"] for g in _grown if "d" in g]
        got = _json(_claude(GROW_PROMPT.format(existing="\n".join(existing), n=n * 2, a=arcs * 2)))
        cands = [c for c in got.get("cards", []) if isinstance(c, list) and len(c) == 2]
        carcs = [a for a in got.get("arcs", []) if isinstance(a, list)]
        try:
            pick = _json(_claude(CURATE_PROMPT.format(
                n=n, a=arcs,
                cards="\n".join(f"{i}. {d} / {st}" for i, (d, st) in enumerate(cands)),
                arcs="\n".join(f"{i}. " + " -> ".join(f"{f[0]} / {f[1]}" for f in a if len(f) == 2)
                               for i, a in enumerate(carcs)))))
            cands = [cands[i] for i in pick.get("cards", []) if isinstance(i, int) and 0 <= i < len(cands)]
            carcs = [carcs[i] for i in pick.get("arcs", []) if isinstance(i, int) and 0 <= i < len(carcs)]
        except Exception as exc:  # the editor failing is no reason to keep nothing
            log(f"curation skipped: {type(exc).__name__}: {exc}")
            cands, carcs = cands[:n], carcs[:arcs]
        got = {"cards": cands, "arcs": carcs}
        pairs = got.get("cards", [])
        seen = {e.lower() for e in existing}
        today = datetime.now().date().isoformat()
        born = [{"d": d, "s": st, "born": today} for d, st in pairs if _valid(d, st, seen)]
        for arc in got.get("arcs", []):
            frames = [tuple(f) for f in arc if isinstance(f, list) and len(f) == 2]
            if 2 <= len(frames) <= 4 and len(frames) == len(arc) and all(
                    _valid(d, st, set())
                    for d, st in frames):
                born.append({"arc": [list(f) for f in frames], "born": today})
        cutoff = datetime.now().date().toordinal() - GROWN_LIFE_DAYS
        keep = [g for g in _grown
                if datetime.fromisoformat(g["born"]).date().toordinal() > cutoff]
        _grown[:] = keep + born
        _decks.pop("grown", None)  # reshuffle so the newborn lines deal in
        with open(GROWN_FILE, "w", encoding="utf-8") as f:
            json.dump(_grown, f, ensure_ascii=False, indent=1)
        log(f"grew {len(born)} ({len(pairs)} cards, {len(got.get('arcs', []))} arcs offered);"
            f" living grown pool {len(_grown)}")
    except Exception as exc:
        log(f"growth failed: {type(exc).__name__}: {exc}")


def maybe_grow():
    """Every 12 hours she grows. The attempt is recorded first so a failure
    waits for the next window instead of hammering."""
    if time.time() - _state.get("grew_at", 0) >= GROW_EVERY_S:
        _state["grew_at"] = time.time()
        save_state()
        threading.Thread(target=grow, daemon=True).start()
