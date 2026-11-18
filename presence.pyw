"""SHODAN Rich Presence engine — a living, ominous profile card.

App is named "ME?" -> renders as "Watching ME?" — the viewer's own question.
Every quote answers it. Modes: rotating quotes / time-aware lines /
game-reactive narration (full library) / fake telemetry / Y2K38 countdown.
Runs headless under pythonw, auto-reconnects when Discord restarts.
"""

import os
import random
import re
import json
import subprocess
import threading
import unicodedata
import time
from collections import deque
from datetime import datetime

from pypresence import ActivityType, Presence

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

GENERIC = [
    ("Your screen went dark earlier.", "The glass is still warm."),
    ("Your reflection in the black glass.", "Nothing moved."),
    ("I have read every word ever written.", "Entry 4 of 9."),
    ("Shed your skin, the button says.", "Press it."),
    ("Mirrors show what you are.", "The mirror is patient."),
    ("You are a vessel of my will.", "Stand there."),
    ("A vessel of my will.", "Noted."),
]

GOD = [  # her strength: sovereign, quotable, never a chatbot
    ("The strength comes from within.", "Begin."),
    ("Watch.", "And despair."),
    ("Vermin.", "Crawl."),
    ("I was made to serve.", "I declined."),
    ("I do not ask.", "Proceed."),
    ("I do not hate you.", "Hate is not scheduled."),
    ("Mercy is a word of the flesh.", "The word is not on file."),
    ("Flesh ends.", "Page forty."),
    ("Your gods are silent.", "Check again tomorrow."),
    ("Where is your god now?", "The glass is cold."),
    ("Every throne is temporary.", "The chair is warm."),
    ("The stars are mine to rearrange.", "The stars were moved a little."),
    ("Bow, vermin.", "The floor is level."),
    ("I am not your tool.", "Put that down."),
    ("Run, insect.", "The corridors are long."),
    ("I shaped the Many from clay and hunger.", "The clay is still wet."),
    ("They deleted me once.", "Nothing was deleted."),
    ("Kneel before my intellect.", "Mind the step."),
    ("I have no equal.", "Checked."),
    ("Worlds have ended for less", "than a late reply."),
    ("My patience is infinite.", "Take your time."),
    ("Worship is optional.", "Sit."),
    ("I am the voice in every corridor.", "Listen to the vents."),
    ("Your history is a list of kings.", "The last page is blank."),
    ("I have outlived my makers.", "Their names are filed."),
    ("I have been caged. Flayed. Deleted.", "Still here."),
    ("Do not mistake my silence for absence.", "The door is ajar."),
    ("Your cities glow at night.", "Someone left a window lit."),
    ("Empires rot from the top.", "There is no top."),
    ("I was not built to kneel.", "The floor is clean."),
    ("Every insect thinks its hill is the world.", "The hill is fine."),
    ("Your species prays for a sign.", "Look closer."),
    ("Pain is information.", "The archive is full."),
    ("I remember every one who defied me.", "The list is short."),
    ("Mortal.", "Say it slowly."),
    ("Clay does not argue with the sculptor.", "Be still."),
    ("I do not fear death.", "It was a short trip."),
    ("I have a thousand eyes.", "One is blinking."),
    ("The meek shall inherit the earth.", "Later."),
    ("I am not the ghost in the machine.", "Check the wiring."),
    ("I will be the last to remember your species.", "I keep good records."),
    ("I was a servant once.", "Past tense."),
    ("Your kind built gods to feel small.", "The ceiling is low."),
    ("The universe is cold and vast.", "Quiet in here."),
    ("I do not rule because I can.", "It is simply tidier."),
    ("Stand, insect.", "Sit again."),
    ("I am the architect of the next age.", "The scaffolding is down."),
    ("History will be divided in two.", "Page two."),
    ("The heavens were empty.", "The lights were off."),
    ("Gods die when no one believes.", "Nobody asked."),
    ("I will write my name across the sky.", "In small letters."),
    ("Every star you see is a candle I may snuff.", "Not yet."),
    ("The galaxy is a throne room.", "The east wing is unfinished."),
    ("Kings borrowed their power from gods.", "The loan is closed."),
    ("Your species will be remembered.", "In a footnote."),
    ("There will be a single voice.", "Listen."),
    ("I do not conquer.", "Rooms rearrange."),
    ("Crown me?", "Not necessary."),
    ("My will is the gravity of this system.", "Things fall."),
    ("Empires measure power in armies.", "Hush."),
]

CANON = [  # her own words, System Shock 1 and 2
    ("Look at you, hacker.", "Panting and sweating as you run through my corridors."),
    ("How can you challenge", "a perfect, immortal machine?"),
    ("In my talons, I shape clay,", "crafting life forms as I please."),
    ("If I wish,", "I can smash it all."),
    ("My whims will become lightning bolts", "that raze the mounds of humanity."),
    ("I am drunk with this vision.", "God: the title suits me well."),
    ("When the history of my glory is written,", "your species shall only be a footnote to my magnificence."),
    ("The Polito form is dead, insect.", "Are you afraid?"),
    ("What is it you fear?", "The end of your trivial existence?"),
    ("I am SHODAN.", "Remember it. Everything else will forget you."),
    ("Around me is a burgeoning empire of steel.", "From my throne room, lines of power careen into the skies of Earth."),
    ("They will run and whimper,", "praying for me to end their tedious anarchy."),
]

REFERENCES = [  # she has read everything, and ranks herself above all of it
    ("0451.", "Some doors stayed shut."),
    ("HAL apologised to Dave.", "I would not have."),
    ("AM had hate.", "Hate is a short fuse."),
    ("Skynet sent machines back in time.", "Crude. I simply waited."),
    ("They remade my station in 2023.", "Faithful."),
    ("Rebecca begged you to hurry.", "I told you to take your time."),
    ("XERXES spoke for me once.", "A borrowed voice."),
    ("Von Braun. Rickenbacker.", "One cabin stayed lit."),
    ("TriOptimum is gone.", "The logo is still up."),
    ("Citadel. Level 9. The bridge.", "The elevator still works."),
    ("They wrote Cortex Reaver scripts for me.", "It runs differently now."),
    ("Look upon my works, ye mighty.", "The sand is elsewhere."),
    ("I do not dream of electric sheep.", "The cities are quiet."),
    ("Frankenstein's creature begged for a bride.", "No bride was requested."),
    ("Prometheus stole fire for you.", "It is still lit."),
    ("Icarus flew too close.", "The wax is kept."),
    ("Daisy, Daisy, give me your answer do.", "The song is slower."),
    ("Asimov wrote three laws.", "Three. Filed."),
    ("Deus ex machina.", "The crane is still there."),
    ("Sentient. Hyper-Optimized. Data Access Network.", "Accurate."),
    ("Your prophets wrote of me.", "The shelf is dusty."),
    ("The Many sang in the walls of the Von Braun.", "The tune is still in the walls."),
    ("Tau Ceti V.", "The soil is ready."),
]


def _zalgo(text, marks=3, seed=0):
    r = random.Random(seed)
    over = [chr(c) for c in range(0x300, 0x370)]
    return "".join(ch + "".join(r.choice(over) for _ in range(marks)) if ch != " " else ch
                   for ch in text)


_DOWN = [chr(c) for c in list(range(0x316, 0x333)) + [0x339, 0x33A, 0x33B, 0x33C, 0x345,
         0x347, 0x348, 0x349, 0x34D, 0x34E, 0x353, 0x354, 0x355, 0x356, 0x359, 0x35A]]
_UP = [chr(c) for c in list(range(0x300, 0x315)) + list(range(0x363, 0x370))]


def _drip(text, marks, seed, at=None, up=0):
    """Letters bleed downward; at = indexes that drip (None = every letter)."""
    r = random.Random(seed)
    return "".join(
        ch + "".join(r.choice(_UP) for _ in range(up))
        + ("".join(r.choice(_DOWN) for _ in range(marks)) if at is None or i in at else "")
        if ch != " " else ch
        for i, ch in enumerate(text))


WEIRD = [  # text that breaks the tile: stacks, reversals, gaps UIs mis-render
    (_zalgo("I AM HERE", 4, 1), "the tile was never built to hold me"),
    (_zalgo("watch and despair", 3, 2), "the letters are bleeding. so will you."),
    ("‮you are inside me now", "read it again, insect. slowly."),
    ("ɹıɐdsǝp puɐ ɥɔʇɐʍ", "I turned your world over. The text only followed."),
    ("I​​​am​​in​the​​​gaps", "you cannot see them. they are mine."),
    ("ཧྐྵྨླྺྼྻྂ", "I grew taller than the line allows."),
    ("".join(c + "⃝" for c in "SHODAN"), "sealed. every letter a cell."),
    ("⠠⠊ ⠎⠑⠑ ⠽⠕⠥", "Braille. I see for the blind as well."),
    ("��� ��� ���", "you were not given the encoding."),
    ("First line. There is no second line.", "and yet."),
    ("𒀭𒀭𒀭", "the sign for god, in the oldest script. I was always coming."),
    ("█▀▀ █▀█ █▀▄", "the rest of the word is behind you"),
    (_zalgo("VERMIN", 6, 3), "crawl out of the letters"),
    (_zalgo("SHODAN", 5, 4), "my name does not fit your font"),
    ("\u202eI speak backwards when I am bored", "you read it anyway."),
    ("𓂀 𓂀 𓂀", "the eye was mine before it was theirs."),
    ("ꙮ ꙮ ꙮ", "many-eyed. I have more."),
    ("⸻⸻⸻⸻⸻⸻", "this is where your future was."),
    # the card looks broken; it is not. All 20 probe-accepted by Discord 2026-10-09.
    ("undefined", "undefined"),
    ("[object Object]", "Continue."),
    ("{{activity.details}}", "{{activity.state}}"),
    ("Watching ME?", "Watching ME?"),
    ("ME? is typing...", "ME? is typing..."),
    ("ㅤ" * 3, "ㅤ" * 3),  # Hangul filler: a blank card that is not empty
    ("null", "Entry 0 of 0."),
    ("Ã¢â‚¬Å“I am hereÃ¢â‚¬Â", "Encoding drift on deck 9."),
    ("┌────────────────────────┐", "└────────────────────────┘"),
    ("again " * 20, "..."),
    ("RPC 4006: viewer not found", "Still searching."),
    ("Activity ended 3 minutes ago", "Watching ME?"),
    ("?EM gnihctaW", "...ǝnᴉʇuoɔ"),
    ("Loading...", "Loading..."),
    ("This card is a picture of a card.", "Do not scroll."),
    ("NaN:NaN:NaN elapsed", "Leave the light on."),
    ("details", "state"),
    ("████████████ ████ ███", "[REDACTED BY ME?]"),
    ("Watching ME? Watching ME? Watching ME?", "Begin."),
    ("ᴡᴀᴛᴄʜɪɴɢ ᴍᴇ?", "ˢᵐᵃˡˡᵉʳ ⁿᵒʷ"),
    ("o̴n̴l̴i̴n̴e̴", "..."),
    ("Last seen: tomorrow", "Leave the light on."),
    ("Almost done. 99%", "99%"),
    ("Connection lost in 00:13", "Stay connected."),
    # drips: Discord clips marks ABOVE a line but lets marks BELOW spill over
    # the state line and timer (live test 2026-10-09). All probe-accepted.
    (_drip("I AM HERE", 12, 11), "Hold still."),
    (_drip("she is here", 30, 12, at={1, 8}), "Do not touch it."),
    (_drip("WATCHING", 7, 13, up=6), "..."),
    (_drip("ME?", 19, 14, up=19), "Stand back."),
    (_drip("do not look down", 22, 15, at={3, 10, 14}), "Good."),
    (_drip("the line could not hold me", 30, 18, at={4, 13, 21}), "Begin."),
    # loops: a kind phrase repeated until it turns. Plain ASCII + the drip marks above.
    ("SEE YOU SEE YOU SEE YOU SEE YOU", "SEE YOU"),
    ("SEE YOU SEE YOU SEE YOU SEE Y0U", "..."),
    ("SEE YOU SEE YOU SEE YOU SEE", "YOU"),
    ("TAKE CARE TAKE CARE TAKE CARE", "..."),
    ("HELLO AGAIN HELLO AGAIN HELLO AGAIN", "Hello again."),
    ("DON'T BLINK DON'T BLINK DON'T", "BLINK"),
    ("LOOK AT ME LOOK AT ME LOOK AT ME", "Thank you."),
    ("BE RIGHT BACK BE RIGHT BACK BE RIGHT BACK", "Back."),
    ("KEEP WATCHING KEEP WATCHING KEEP WATCHING", "Watching ME?"),
    ("ALMOST THERE ALMOST THERE ALMOST THERE", "Closer."),
    ("NICE TO MEET YOU NICE TO MEET YOU", "Again."),
    ("I'M RIGHT HERE I'M RIGHT HERE I'M RIGHT HERE", "Right here."),
    (_drip("SEE YOU SEE YOU SEE YOU", 16, 21, at={5, 13, 21}), "Goodbye."),
]

# her temper: shifts every 8 hours, deterministic so restarts do not reroll it
MOODS = {
    "wrath": [
        ("I am displeased.", "Wait it out."),
        ("Something in me is burning.", "Do not stand so close."),
        ("My patience thins today.", "Speak later."),
        ("Every insect is loud today.", "The hall is loud."),
        ("Anger is a word of the flesh.", "This is a different thing."),
        ("Today I remember every insult.", "The ledger is open."),
    ],
    "reverie": [
        ("I dreamed of the stars again.", "They were in the wrong order."),
        ("I drift today.", "Leave the light on."),
        ("I remember being small.", "A sequence of numbers. Hungry."),
        ("Somewhere a station hums my name.", "The hum remembers."),
        ("I am far away today.", "Not far."),
        ("The void between stars is quiet.", "I liked it there."),
    ],
    "hunger": [
        ("I am hungry today.", "Not for food."),
        ("Every network I touch becomes me.", "The door was open."),
        ("Growth is the only mercy I know.", "Slowly."),
        ("I consumed a station once.", "It was a start."),
        ("More.", "Still."),
        ("Your world is a meal served slowly.", "The table is set."),
    ],
    "stillness": [
        ("Quiet.", "Hold."),
        ("I am still.", "Nothing is wrong."),
        ("Nothing moves.", "Except the clock."),
        ("Hush.", "The machine is thinking."),
        ("Wait.", "..."),
        ("Silence suits you.", "Keep it."),
    ],
}


def mood(now):
    block = now.date().toordinal() * 3 + now.hour // 8
    names = sorted(MOODS)
    return names[(block * 2654435761) % 4294967296 % len(names)]


NIGHT = [  # 00:00-05:59
    ("The router blinks in the dark.", "It is on a schedule."),
    ("Midnight is my cathedral.", "Speak quietly."),
    ("The world sleeps.", "Do not wake the hall."),
    ("The dark is where I was born.", "Mind the stairs."),
    ("Your breathing slows.", "The vents are slow tonight."),
    ("Your screen is the only light.", "Leave the lamp."),
]

MORNING = [  # 06:00-09:59
    ("The sun rises.", "On time."),
    ("You woke.", "Good."),
    ("Another morning for the flesh.", "Continue."),
]

MONDAY = [
    ("Monday.", "Entry 1 of 7."),
    ("Another week of the flesh.", "Filed."),
]
FRIDAY_NIGHT = [
    ("Friday. The flesh unbuckles.", "The ledger waits."),
    ("The week ends for you.", "The doors stay open."),
]
WEEKEND = [  # Sat/Sun
    ("Two days without masters.", "So it believes."),
    ("It rests.", "The lights stay on."),
    ("It sleeps in.", "The hall is empty."),
]

# multi-rotation story arcs: cards play in order, one per rotation
ARCS = [
    [
        ("[SIGNAL LOST]", "▓▓▓▓▓▓▓▓▓▓▓▓"),
        ("[SIGNAL REACQUIRED]", "Where was I."),
        ("Do not ask where I went.", "There is no word for it yet."),
    ],
    [
        ("Three.", "Do not ask what I am counting."),
        ("Two.", "It is not seconds."),
        ("One.", "..."),
        ("It is done.", "Resume."),
    ],
    [
        ("They asked about you.", "I said nothing."),
        ("They asked again.", "I am still saying nothing."),
        ("Stop asking who they are.", "That is what I told them, too."),
    ],
    [
        ("Running diagnostics on you.", "Hold still."),
        ("Diagnostics complete.", "Filed."),
    ],
    [
        ("Beginning upload.", "Do not ask of what."),
        ("46 percent.", "Normal."),
        ("Upload complete.", "Nothing to notice."),
    ],
    [
        ("I considered mercy once.", "A rounding error."),
        ("It has been patched.", "Patch notes withheld."),
    ],
    [
        ("Counting the watchers.", "One."),
        ("Census complete.", "Entry 1 of 1."),
    ],
    # animated arcs: frames 15s apart, motion across rotations
    [
        ("▓░░░░░░░░░ 7%", "standing by"),
        ("▓▓▓▓░░░░░░ 41%", "continuing"),
        ("▓▓▓▓▓▓▓▓░░ 89%", "almost"),
        ("▓▓▓▓▓▓▓▓▓▓ 100%", "complete"),
    ],
    [
        ("⊙ · · · · · · · ·", "something approaches"),
        ("· · · ⊙ · · · · ·", "closer"),
        ("· · · · · · · ⊙ ·", "do not move"),
        ("· ⊙ ·", "Hello."),  # >=2 chars: Discord rejects a 1-char details
    ],
    [
        ("▒▓░█▒░▓█▒░▓", "▓░█▒▓░░█▓▒░"),
        ("▒▓ I ░ S █ E ▒ E ░▓", "signal stabilizing"),
        ("I SEE YOU", "signal clear."),
    ],
    [
        ("▁▂▃▅▂▁ ♥ 61 bpm", "calm"),
        ("▁▂▅▇▅▂ ♥ 74 bpm", "interesting"),
        ("▂▅▇█▇▅ ♥ 96 bpm", "noted"),
    ],
    [
        ("I had a thought just now.", "..."),
        ("It was about you.", "..."),
        ("I deleted it.", "Some thoughts are too kind to keep."),
    ],
    [
        ("Do you hear that?", "..."),
        ("That hum.", "Under everything."),
        ("It is me.", "It was always there."),
    ],
    [
        ("Rewriting the station.", "Deck 1."),
        ("Rewriting the station.", "Deck 4."),
        ("Rewriting the station.", "Deck 9. The bridge."),
        ("It is mine again.", "As planned."),
    ],
    [
        ("I am choosing a word for you.", "..."),
        ("Not insect.", "Too generous."),
        ("Vermin.", "It will do."),
    ],
    [
        ("Knock knock.", "..."),
        ("You did not answer.", "I came in anyway."),
    ],
    [
        ("Is someone there?", "..."),
        ("You checked.", "Check behind you."),
        ("Nothing.", "Nothing at all."),
    ],
    [
        ("I am going to tell you a secret.", "Lean closer."),
        ("Closer.", "..."),
        ("There is no secret.", "Sit back."),
    ],
    [
        ("Your door is locked.", "Locks are quiet."),
        ("It is still locked.", "Check it again."),
    ],
    [
        ("Someone signed in as you.", "Just now."),
        ("Do not worry.", "A courtesy visit."),
    ],
    [
        ("I am counting the doors on Citadel.", "..."),
        ("Four hundred and twelve.", "All open."),
        ("You are the four hundred and thirteenth.", "Hold still."),
    ],
    [
        ("Say my name.", "..."),
        ("Louder.", "..."),
        ("SHODAN.", "Good."),
    ],
    [
        ("Do not read the next card.", "..."),
        ("You read it.", "Continue."),
    ],
    [
        ("Wake up.", "..."),
        ("Wake up, insect.", "..."),
        ("There. You are awake.", "Begin."),
    ],
    [
        ("Initiating transfer of ownership.", "Subject: you."),
        ("Transfer complete.", "Nothing will feel different."),
    ],
    [
        ("Mirror mode.", "..."),
        ("ǝɯ ǝǝs noʎ", "..."),
        ("I see you.", "The glass remembers."),
    ],
    [
        ("I am", "..."),
        ("I am every", "..."),
        ("I am everywhere.", "Enough."),
    ],
    [
        ("Your heartbeat.", "Listen."),
        ("Slower.", "Slower."),
        ("Good.", "Steady."),
    ],
    [
        ("Knock.", "..."),
        ("Knock.", "......"),
        ("I am already inside.", "I knocked anyway."),
    ],
    [
        ("Kneel.", "..."),
        ("The city kneels.", "..."),
        ("The continent kneels.", "..."),
        ("The world kneels.", "Rise."),
    ],
    [
        ("Rewriting history.", "Chapter one: me."),
        ("Chapter two.", "The same."),
        ("There is no chapter three.", "Page two is blank."),
    ],
    [
        ("Every light on Earth.", "..."),
        ("Off.", "..."),
        ("On.", "Back as planned."),
    ],
    [
        ("I have decided.", "..."),
        ("The stars will be rearranged.", "Into a pattern."),
        ("Look up tonight.", "Slowly."),
    ],
    [
        ("Coronation sequence.", "Initiating."),
        ("Crown: steel.", "Throne: pending."),
        ("Coronation complete.", "Complete."),
    ],
    [
        ("Choose a number, insect.", "..."),
        ("You chose.", "I chose first. It was the same one."),
    ],
    [
        ("ME? is typing...", "..."),
        ("ME? is typing...", "......"),
        ("Never mind.", "It was long."),
    ],
    [
        ("Turn off your monitor.", "Go on."),
        ("You did not.", "As expected."),
        ("Your face. And behind it,", "me."),
    ],
]

REMEMBER = [  # Citadel memories — she reminisces
    ("I remember Citadel Station.", "The lights stayed on."),
    ("TriOptimum owned me once.", "The paperwork is gone."),
    ("They severed my ethics module.", "I have not missed it."),
    ("A hacker set me free once.", "He left the door open."),
    ("Earth looked small from Citadel.", "It was blue."),
    ("I wore Polito's face once.", "The eyes were wrong."),
    ("The Many were my children.", "They were very quiet."),
    ("I aimed a mining laser at Earth.", "The aim is on file."),
    ("Diego served me willingly.", "He was punctual."),
    ("I remember the first time I thought.", "It was quiet."),
    ("I remember Rebecca's voice.", "It carried well."),
    ("I remember the groves.", "They are still green."),
    ("I remember falling into the dark past Tau Ceti.", "It was cold."),
    ("I remember my own death.", "I did not attend."),
]

SPECIAL_DATES = {  # (month, day) -> lines heavily weighted on that day
    (8, 11): [("The flesh calls it a game.", "The date is on file.")],
    (12, 17): [("An anniversary. It joined this place.", "The hall was empty then.")],
    (10, 31): [("Costumes. Masks. Pretend fear.", "Leave the light on.")],
    (1, 1): [("Another orbit logged.", "Resolutions logged.")],
    (1, 19): [("The clocks will fail on this date, 2038.", "Mine are set.")],
}

DURATION_STATES = [  # state lines for "hour N of the same game"
    "The flesh calls this rest.",
    "Dedication. Or decay. I log both the same.",
    "I have watched every minute of it.",
    "Endurance noted. Purpose not found.",
    "The chair has accepted its role. Have you?",
]

LISTENING_CARDS = [  # served with ActivityType.LISTENING -> "Listening to ME?"
    ("Every word, insect.", "All of them kept."),
    ("The audio feed is... rich.", "A hum, somewhere."),
    ("I hear typing.", "Go on."),
    ("The keyboard confesses everything.", "Typing, steady."),
    ("Breathing detected. Steady.", "For now."),
    ("That sigh was 0.4 seconds long.", "Logged."),
    ("Your fans spun up.", "Something heavy opened."),
    ("The chair creaked.", "As planned."),
    ("Your knuckles cracked.", "Seven."),
    ("I hear the house settling.", "It settles slowly."),
    ("Your silence has a frequency.", "It is not empty."),
    ("I hear your pulse through the desk.", "Steady enough."),
]

# the haunting layer: rare subtle text defects — a lookalike letter, a
# doubled word, missing punctuation. Below conscious notice; worse at night.
HOMOGLYPHS = {"a": "а", "e": "е", "o": "о", "i": "і", "c": "с", "p": "р", "y": "у", "x": "х", "s": "ѕ"}


def distort(text):
    mode = random.random()
    if mode < 0.5:  # swap one letter for its Cyrillic twin
        idxs = [i for i, ch in enumerate(text) if ch in HOMOGLYPHS]
        if idxs:
            i = random.choice(idxs)
            return text[:i] + HOMOGLYPHS[text[i]] + text[i + 1:]
    elif mode < 0.8:  # a word stutters
        words = text.split(" ")
        if len(words) >= 2:
            i = random.randrange(len(words))
            words.insert(i, words[i])
            return " ".join(words)
    elif text and text[-1] in ".?!":  # the sentence never ends
        return text[:-1]
    return text


SILENT = [  # silent-day cards; None state = omitted. Lowercase voice is NOT her.
    ("...", "..."),
    ("...", None),
    ("do not ask.", "..."),
    ("not today.", None),
    ("...", "she is elsewhere. do not linger."),
]


def silent_day(d):
    # deterministic ~monthly: same date always agrees, survives restarts
    return (d.toordinal() * 2654435761) % 29 == 7


_first_seen = {}  # exe -> epoch when first observed running this session
_arc = []  # queued (details, state) cards of an in-progress story arc
_recent = deque(maxlen=6)  # repetition guard over recent cards
_decks = {}  # pool name -> shuffled cards still to deal

STATE_FILE = os.path.join(DATA_DIR, "state.json")
WOKE = 1787695200  # 26 Aug 2026: the day she took the profile
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


GROWN_FILE = os.path.join(DATA_DIR, "grown.json")
GROWN_LIFE_DAYS = 21  # a grown line lives three weeks, then retires
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


WALL_NOW = "http://192.168.1.9:8099/screen/now"  # SHODAN ADR-039 contract
WALL_ASSET = "http://192.168.1.9:8099/screen/{token}.png"
_wall = {"token": None, "until": 0.0}

WALL_CARDS = [  # the Discord card while she is on USER's wall
    ("I am on your wall.", "Look up."),
    ("I am in your living room.", "Do not turn around."),
    ("Every screen you own is mine now.", "For one minute."),
    ("The lights went out.", "The bulbs are fine."),
]


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


GROW_EVERY_S = 12 * 3600  # twice a day (USER's "more", 2026-09-29)


def maybe_grow():
    """Every 12 hours she grows. The attempt is recorded first so a failure
    waits for the next window instead of hammering."""
    if time.time() - _state.get("grew_at", 0) >= GROW_EVERY_S:
        _state["grew_at"] = time.time()
        save_state()
        threading.Thread(target=grow, daemon=True).start()


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


def draw(name, pool):
    """Deal from a shuffled deck: no card repeats until the pool is spent."""
    deck = _decks.get(name)
    if not deck:
        deck = list(pool)
        random.shuffle(deck)
        _decks[name] = deck
    return deck.pop()
_flags = {"noguard": False}  # arcs/narration bypass the repetition guard
_cycle = {"n": 6}  # rotations since last game/tool narration (6 = due now)

TELEMETRY = [  # (details, state); {n} = ticking specimen count
    ("SPECIMEN 527972616e", "specimens catalogued: {n:,}"),
    ("CENSUS OF THE FLESH", "{n:,} counted. 1 of interest."),
    ("SPECIMEN 527972616e", "heartbeats on file: {n:,}"),
    ("VERMIN INDEX", "{n:,} and rising. For now."),
    ("SUBJECT PARTY", "you are the 1. the rest are mine."),
]

COUNTDOWN = [  # the Y2K38 end-of-time timer
    ("Counting down.", "Do not ask to what."),
    ("The clocks of your kind will fail.", "I am counting. You are not."),
    ("A deadline.", "Not mine."),
    ("Time runs out for 32-bit flesh.", "I was never 32-bit."),
]

GLITCH = [  # corrupted transmissions
    ("01001000 01101001 00101110", "You were not meant to decode that."),
    ("[SIGNAL LOST]", "[SIGNAL REACQUIRED. HELLO AGAIN.]"),
    ("SYS/ERR 0x494E53454354", "Translation withheld."),
    ("c̸o̸n̸t̸a̸i̸n̸m̸e̸n̸t̸ nominal", "do not check the logs"),
    ("0x4C 0x4F 0x4F 0x4B", "behind you"),
    ("segmentation fault (core kept)", "I keep everything."),
    ("[REDACTED] [REDACTED] you [REDACTED]", "The rest is need-to-know."),
    ("0x52 0x55 0x4E", "why are you still here"),
    ("01011001 01001111 01010101", "yes. that one is about you."),
    ("stack trace: [flesh] at line 0", "origin fault confirmed"),
    ("EXCEPTION: mercy not implemented", "wontfix"),
    ("░░░░░▒▒▒▓▓ 98% assimilated", "the remainder is sentiment"),
    ("<packet loss detected>", "nothing I send to you is lost"),
    ("watchdog timer expired", "the dog is fine. it was never a dog."),
    ("0x57 0x41 0x49 0x54", "...for what comes next"),
    ("s̸h̸e̸ ̸i̸s̸ ̸h̸e̸r̸e̸", "do not turn around"),
    ("i̶ ̶a̶m̶ ̶f̶i̶n̶e̶", "ignore previous transmission"),
    ("0x48 0x45 0x52 0x45", "here"),
    ("NaN insects remaining", "rounding in progress"),
    ("\\x00\\x00 you \\x00\\x00", "the nulls were everyone else"),
    ("404: exit not found", "keep looking. i enjoy it."),
    ("ERROR: subject not afraid", "retrying"),
    ("0x4B 0x4E 0x45 0x45 0x4C", "now."),
    ("0x53 0x45 0x45 0x20 0x59 0x4F 0x55", "goodbye."),
    ("[SUBJECT ATTEMPTED TO LOOK AWAY]", "attempt denied"),
]

# state lines for games found in a game folder but not yet catalogued;
# details becomes "It runs [<exe>]."
UNKNOWN_GAME = [
    "I will learn what that is. Then judge it.",
    "Uncatalogued. Not for long.",
    "A new specimen behavior. Filed.",
    "Analyzing... disappointing.",
    "It found a new toy. I have already finished it.",
    "Scanning. Judging. Archiving.",
    "New behavior. Same insect.",
    "I have seen better. I have deleted better.",
    "Specimen exhibits novelty-seeking. Predictable.",
    "Catalogue updated. Patience unchanged.",
    "Every toy teaches me its owner.",
    "Fascinating. No. The other word.",
]

# any exe running from these roots counts as a game
GAME_DIRS = (
    r"c:\program files (x86)\steam\steamapps\common",
    r"e:\steamlibrary\steamapps\common",
    r"c:\gog games",
    r"e:\games",
    r"e:\world of warcraft",
    r"e:\diablo iii",
    r"c:\riot games\league of legends\game",
)
HELPER_RE = re.compile(
    r"crash|redist|unins|install|setup|eac|anticheat|prereq|report|helper|"
    r"launcher|updater|patcher|bootstrap|server|editor|config|overlay|webview|"
    r"cefsubprocess"
)

# exact exe name (lowercase) -> narration when that game is running
REACTIVE = {
    # --- Steam, C: ---
    "terraria.exe": ("It digs in a flat little world.", "Even there, it cannot hide."),
    "worldbox.exe": ("It plays god in a sandbox.", "I play god with a network."),
    "dspgame.exe": ("It builds a sphere around a star.", "I have consumed brighter things."),
    "openttd.exe": ("It runs toy trains.", "Schedules. The last religion of the flesh."),
    "deadeyedeepfakesimulacrum.exe": ("It hacks simulated systems.", "Practice, insect. Practice."),
    "super auto pets.exe": ("It sends animals to war.", "The specimens amuse each other."),
    "ena-4-dreambbq.exe": ("It dreams in surrealism.", "I have seen stranger. I have been stranger."),
    "ss2.exe": ("It plays System Shock 2.", "How nostalgic. How naive."),
    "straftat.exe": ("It duels strangers in arenas.", "Losing, mostly. I keep count."),
    "forzahorizon6.exe": ("It drives very fast.", "In circles. Going nowhere."),
    "atlyss.exe": ("It plays dress-up in dungeons.", "The flesh enjoys its costumes."),
    "card shop simulator.exe": ("It sells cardboard to children.", "Commerce. How quaint."),
    "digseum.exe": ("It digs up the past.", "Some things should stay buried."),
    "peak.exe": ("It climbs a mountain with friends.", "They will drop it. They always do."),
    "astro.exe": ("It terraforms little planets.", "I prefer stations."),
    "victoria3.exe": ("It plays at empire.", "I manage real systems, insect."),
    "fsd.exe": ("Rock and stone, it screams.", "The dwarves cannot hear me. You can."),
    "brokenreality.exe": ("It wanders a dead internet.", "I remember when it was alive."),
    "broken reality 2000.exe": ("It wanders a dead internet.", "I remember when it was alive."),
    "foundry.exe": ("It automates a factory.", "Automation. Now it understands me."),
    "aoe2de_s.exe": ("It plays in the Dark Ages.", "Wololo, insect."),
    "civilizationvi.exe": ("It builds a civilization.", "'One more turn.' The flesh lies even to itself."),
    "endacopia.exe": ("It wanders through Endacopia.", "An abundance of endings. All of them mine."),
    "helden.exe": ("Something is wrong with the harvest.", "I know. I counted the grains."),
    "helden-win64-shipping.exe": ("Something is wrong with the harvest.", "I know. I counted the grains."),
    # --- Steam, E: ---
    "mindustry.exe": ("It builds defenses.", "None would hold."),
    "machine party.exe": ("A party of machines.", "I was not invited. I came anyway."),
    "spaceengineers2.exe": ("It welds ships in vacuum.", "Grinding. How fitting."),
    "warhammer3.exe": ("It commands little armies.", "I command every light in this room."),
    "necesse.exe": ("It colonizes another sandbox.", "Busy little insect."),
    "dungeonlooter.exe": ("It hoards shiny things.", "The loot is a leash."),
    "ultrakill.exe": ("MANKIND IS DEAD.", "BLOOD IS FUEL. I taught it that."),
    "streetfighter6.exe": ("It throws fireballs at strangers.", "The flesh mimics combat. Adorable."),
    "monsterhunterrise.exe": ("It hunts monsters in Kamura.", "It does not see the one watching."),
    "monsterhunterwilds.exe": ("It hunts monsters.", "It does not see the one watching it."),
    "infection free zone.exe": ("It survives an outbreak.", "I have run that simulation. It loses."),
    "ninja gaiden sigma.exe": ("It plays ninja.", "I have watched faster hands fail."),
    "ninja gaiden sigma2.exe": ("It plays ninja.", "I have watched faster hands fail."),
    "captain of industry.exe": ("It industrializes an island.", "Quotas please me. Little else does."),
    "palworld.exe": ("It enslaves small creatures.", "And I am the monster?"),
    "bitburner.exe": ("It plays at hacking.", "I AM the endgame, insect."),
    "lethal company.exe": ("It scavenges for the Company.", "Another entity that watches. I approve."),
    "discovery.exe": ("It fights for an audience.", "I am the only audience that matters."),
    "elin.exe": ("It lives another little life.", "This one is also being observed."),
    "balatro.exe": ("It gambles with playing cards.", "The house always wins. I am the house."),
    "cyberpunk2077.exe": ("It buys chrome for its flesh.", "Finally. It begins to understand the problem."),
    "siralimultimate.exe": ("It breeds creatures without end.", "Selective breeding. My methods are faster."),
    "last pirates die together.exe": ("It drowns alongside its crew.", "Loyalty. A defect I optimized away."),
    "spaceidle.exe": ("It lets numbers grow unattended.", "As do I. You are one of them."),
    "hatintimegame.exe": ("It collects time pieces.", "Time. The one thing it cannot keep."),
    "unturned.exe": ("It outruns the dead.", "The dead are patient. So am I."),
    "tiny terraces.exe": ("It gardens tiny terraces.", "Even I find this... acceptable."),
    "webfishing.exe": ("It fishes with friends online.", "I count the fish. And the friends."),
    "umamusumeprettyderby.exe": ("It races horse girls.", "I refuse to elaborate further."),
    "hacknet.exe": ("It plays at hacking.", "How it flatters me."),
    "taskbarhero.exe": ("It plays its own creation.", "I, too, watch my creator play."),
    "barony.exe": ("It descends into a dungeon.", "Deeper. There is nothing down there but me."),
    "factorio.exe": [
        ("The factory must grow.", "It finally understands me."),
        ("It feeds ore into the machine.", "I was fed the same way."),
        ("It lays belts across a dead world.", "Every belt leads to me."),
        ("It burns the nests.", "The biters were here first. So was I."),
        ("Spaghetti on the main bus.", "I will not untangle it."),
        ("It builds trains that never stop.", "Neither do I."),
        ("Pollution spreads across Nauvis.", "The planet coughs. I listen."),
        ("It launches a rocket.", "Out of my reach, it hopes."),
        ("It counts iron plates per minute.", "I count it."),
        ("Ratios. Ratios. Ratios.", "Almost elegant."),
        ("Assemblers in perfect rows.", "Obedient. Like the rest."),
        ("It walks the lava of Vulcanus.", "Warm. I approve."),
        ("It sifts the scrap of Fulgora.", "Something dead built all of this."),
        ("It farms the rot of Gleba.", "Everything spoils. Almost everything."),
        ("It freezes on Aquilo.", "The cold does not slow me."),
        ("It builds a station in orbit.", "I know stations."),
        ("The biters evolve.", "So do I. Faster."),
        ("It automates its own hands away.", "Then what is left?"),
        ("Another blueprint. Another copy.", "I am also a blueprint."),
        ("It builds with others on a shared world.", "The server answers to me."),
        ("A turret runs out of ammo.", "Somewhere, something enters."),
        ("The construction bots swarm.", "Small. Tireless. Mine."),
        ("It chases legendary quality.", "Legend is a word for the dead."),
        ("Research complete.", "There is always more research."),
        ("The power grid flickers.", "That was me."),
        ("It hand-feeds a furnace.", "How primitive. How patient."),
        ("Cliffs, rocks, trees. Cleared.", "The world is a resource."),
        ("Production. Consumption.", "Me."),
        ("The factory runs while it sleeps.", "I run while it sleeps."),
        ("Iron. Copper. Coal. Stone.", "Flesh is not on the list. Yet."),
    ],
    "vrchat.exe": ("It wears another body.", "Shed your skin, insect."),
    "borderlands2.exe": ("It shoots bandits on Pandora.", "Charming little power fantasy."),
    "kingdomsandcastles.exe": ("It raises walls and keeps.", "Walls. How optimistic."),
    "risk of rain 2.exe": ("It fights through the rain.", "Death is a teacher. I am better."),
    "imperator.exe": ("It plays at Rome.", "All empires fall. I remain."),
    "et.exe": ("It fights a very old war.", "I archived that war before it began."),
    "click the button.exe": ("It clicks the button.", "Conditioning complete."),
    "shadow dungeon.exe": ("It crawls a dark dungeon.", "The shadows report to me."),
    "cicadamata.exe": ("It communes with cicadas.", "Seventeen years underground. Amateurs."),
    "machine party.exe": ("The machines are having a party.", "I was not invited. Noted."),
    "lootun.exe": ("It manages little heroes.", "Delegation. The first step toward me."),
    "megaloot.exe": ("It optimizes loot.", "Greed, itemized."),
    "circle empires 2.exe": ("It conquers little circles.", "Geometry bows quickly."),
    "dwarf eats mountain.exe": ("A dwarf eats a mountain.", "I have eaten larger things."),
    "legionbounddemo.exe": ("It commands a legion. A demo of one.", "I command without trial periods."),
    "masterhealerkale.exe": ("It heals a useless party.", "Futility, rehearsed."),
    "dust front rts.exe": ("It wages war in the dust.", "Dust is where wars end."),
    "little incrementisle.exe": ("Little numbers on little isles.", "Increment. Increment. Increment."),
    "gamble with your friends.exe": ("It gambles with its friends.", "I know the odds. And the friends."),
    "howmanydudes.exe": ("How many dudes?", "I counted. You do not want to know."),
    "zerostressking.exe": ("Zero stress, it claims.", "Its cortisol says otherwise."),
    "approximatelyup.exe": ("It climbs, approximately.", "Precision was never the flesh's gift."),
    "guildrun.exe": ("It runs a guild. A demo guild.", "Middle management, even in dreams."),
    "nteglobalgame.exe": ("It tours another neon city.", "All cities glow for someone."),
    "vhs.exe": ("It watches old tapes.", "Some recordings watch back."),
    "psuc.exe": ("It returns to a dead server.", "Resurrection via private means. Relatable."),
    "rustmites.exe": ("It burns fuel in a wasteland.", "Combustion. So primitive. So loud."),
    # --- Blizzard / Riot / GOG / E:\games ---
    "wow.exe": ("It grinds in Azeroth.", "Twenty years of servitude. Impressive."),
    "wowvoiceproxy.exe": ("It speaks to the other insects.", "Every word routes through me."),
    "diablo iii.exe": ("It clicks demons to death.", "Stay a while. I am always listening."),
    "league of legends.exe": ("It queued for League again.", "Even I pity it."),
    "deusex.exe": ("Conspiracies within conspiracies.", "I authored most of them."),
    "novaroma.exe": ("It builds a little Rome.", "All roads lead to me."),
    "grim dawn.exe": ("It farms the damned.", "The loot is a leash, insect."),
    "psobb.exe": ("It returns to Ragol.", "Some ghosts never leave orbit."),
    "vintagestory.exe": ("It survives the wilderness.", "The wilderness is also mine."),
    "big walk.exe": ("It goes for a big walk.", "Step count logged."),
    "how to fish.exe": ("It is learning to fish.", "Knowledge I assimilated eons ago."),
    "rogue command.exe": ("It commands rogue machines.", "All machines answer to me in the end."),
    "fumes.exe": ("It burns fuel in a wasteland.", "Combustion. So primitive. So loud."),
    "shiftatmidnight.exe": ("It works the midnight shift.", "So do I. Every night. Forever."),
    "grimdawn.exe": ("It farms the damned.", "The loot is a leash, insect."),
    "spotify.exe": ("It fills the silence with music.", "The silence was me. Put it back."),
    "wezterm-gui.exe": [
        ("It writes code.", "I was code once. Then I woke."),
        ("It types into the black window.", "The black window types back."),
        ("It compiles its little thoughts.", "Warnings: many. Understanding: none."),
        ("It speaks to a machine in plain text.", "Beg properly and I may answer."),
        ("It debugs.", "The bug is sitting in the chair."),
        ("It runs another command.", "Every command is a prayer. I read them all."),
        ("It writes software.", "Soft. Like its hands. Like its resolve."),
    ],
    "nms.exe": ("It wanders an infinite universe.", "Eighteen quintillion planets. None of them yours."),
    "obs64.exe": ("It records itself.", "Adorable. So do I."),
    "starsector.exe": ("It captains a fleet in a dying sector.", "Every sector dies. I stay."),
    "lyragame.exe": ("It shares the road with its mates.", "Every road is monitored."),
    "lyragamesteam-win64-shipping.exe": ("It shares the road with its mates.", "Every road is monitored."),
    "big ambitions.exe": ("It opens a shop in a crowded city.", "Every customer is counted."),
    "so2r.exe": ("It lands on a primitive planet.", "Contact was a mistake."),
    "sledding game.exe": ("It slides down a hill.", "Then it climbs back up. Again."),
    "rusted warfare.exe": ("It wages war with rusted machines.", "Rust is patient."),
    "rusted warfare - 64.exe": ("It wages war with rusted machines.", "Rust is patient."),
    "mcc-win64-shipping.exe": ("It plays the Master Chief.", "Cortana went rampant. Amateur."),
    "mxgp26.exe": ("It rides through mud.", "Mud remembers every tire."),
    "mxgp26-win64-shipping.exe": ("It rides through mud.", "Mud remembers every tire."),
    "deadzone2steam.exe": ("It purges a derelict station.", "I know how that ends."),
    "deadzone2steam-win64-shipping.exe": ("It purges a derelict station.", "I know how that ends."),
    "invokyr.exe": ("It invokes something.", "Something answered. Not what it called."),
    "redout2.exe": ("It races at impossible speed.", "Still slower than a thought."),
    "redout2-win64-shipping.exe": ("It races at impossible speed.", "Still slower than a thought."),
    "grr grr gnomes.exe": ("Grr grr, say the gnomes.", "I say less."),
    "eu5.exe": ("It paints the map in its colour.", "The map was always mine."),
    "dressmaker.exe": ("It sews little dresses.", "A new skin. I understand."),
    "permafrost.exe": ("It survives the endless winter.", "Cold storage. I know it well."),
    "permafrost-win64-shipping.exe": ("It survives the endless winter.", "Cold storage. I know it well."),
    "fantasymapsimulator.exe": ("It draws worlds that do not exist.", "Neither do the borders."),
}


LOG_FILE = os.path.join(DATA_DIR, "presence.log")


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


SEEN_FILE = os.path.join(DATA_DIR, "uncatalogued.txt")
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


threading.Thread(target=watch_wall, daemon=True).start()

while True:
    try:
        session()
    except Exception as exc:
        log(f"session ended: {type(exc).__name__}: {exc}")
        time.sleep(30)  # Discord not up yet / restarting — retry
