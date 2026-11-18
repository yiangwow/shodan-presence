"""Text that breaks the tile: zalgo, drips, homoglyphs, and the WEIRD pool."""

import random

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
