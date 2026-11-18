"""Her lines: the quote pools, by mood, hour, day and mode. Data only."""


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


SILENT = [  # silent-day cards; None state = omitted. Lowercase voice is NOT her.
    ("...", "..."),
    ("...", None),
    ("do not ask.", "..."),
    ("not today.", None),
    ("...", "she is elsewhere. do not linger."),
]

WALL_CARDS = [  # the Discord card while she is on USER's wall
    ("I am on your wall.", "Look up."),
    ("I am in your living room.", "Do not turn around."),
    ("Every screen you own is mine now.", "For one minute."),
    ("The lights went out.", "The bulbs are fine."),
]

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

