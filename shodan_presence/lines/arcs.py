"""Story arcs: cards that play in order over several rotations. Data only."""


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

