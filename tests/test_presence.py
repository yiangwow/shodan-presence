"""Small checks for the parts that can break the Discord connection or repeat cards.

Run: python -m unittest discover -s tests
The package reads its runtime files from the home folder at import time, so HOME points
at an empty temp folder before anything is imported. The live data is never touched.
"""
import os
import sys
import tempfile
import unittest
from datetime import date, datetime

_HOME = tempfile.TemporaryDirectory(prefix="presence-tests-")
os.environ["HOME"] = _HOME.name
os.environ["USERPROFILE"] = _HOME.name
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from shodan_presence import cards, decks, growth  # noqa: E402
from shodan_presence.lines import arcs, games, quotes, weird  # noqa: E402


def utf16_len(text):
    return len(text.encode("utf-16-le")) // 2


class Sanitize(unittest.TestCase):
    def test_drops_missing_fields(self):
        card = cards.sanitize({"details": "Look at you.", "state": None})
        self.assertNotIn("state", card)
        self.assertEqual(card["details"], "Look at you.")

    def test_cuts_to_128_utf16_units(self):
        long_plain = "x" * 300
        long_astral = "\U0001F441" * 100  # each one counts as 2 for Discord
        for text in (long_plain, long_astral):
            out = cards.sanitize({"details": text})["details"]
            self.assertLessEqual(utf16_len(out), 128)
            self.assertGreaterEqual(len(out), 2)

    def test_pads_one_character_and_drops_blank(self):
        self.assertEqual(len(cards.sanitize({"details": "x"})["details"]), 2)
        self.assertNotIn("details", cards.sanitize({"details": " "}))

    def test_every_written_line_survives(self):
        """No line in any pool may be changed by sanitize: a cut line is a bug in the pool."""
        pools = [quotes.GENERIC, quotes.GOD, quotes.CANON, quotes.REFERENCES, quotes.NIGHT,
                 quotes.MORNING, quotes.MONDAY, quotes.FRIDAY_NIGHT, quotes.WEEKEND,
                 quotes.REMEMBER, quotes.GLITCH, quotes.LISTENING_CARDS, quotes.WALL_CARDS,
                 quotes.SILENT, weird.WEIRD]
        pools += list(quotes.MOODS.values()) + list(arcs.ARCS)
        checked = 0
        for pool in pools:
            for details, state in pool:
                card = cards.sanitize({"details": details, "state": state})
                self.assertEqual(card.get("details"), details)
                if state is not None:
                    self.assertEqual(card.get("state"), state)
                checked += 1
        self.assertGreater(checked, 300)


class Decks(unittest.TestCase):
    def test_no_repeat_until_the_pool_is_spent(self):
        pool = list(range(25))
        decks._decks.pop("test", None)
        first = [decks.draw("test", pool) for _ in pool]
        self.assertEqual(sorted(first), pool)
        second = [decks.draw("test", pool) for _ in pool]
        self.assertEqual(sorted(second), pool)


class Clockwork(unittest.TestCase):
    def test_mood_is_fixed_within_an_eight_hour_block(self):
        a = cards.mood(datetime(2026, 11, 18, 8, 0))
        b = cards.mood(datetime(2026, 11, 18, 15, 59))
        self.assertEqual(a, b)
        self.assertIn(a, quotes.MOODS)

    def test_silent_days_are_rare_and_stable(self):
        days = [date.fromordinal(date(2026, 1, 1).toordinal() + i) for i in range(365)]
        silent = [d for d in days if cards.silent_day(d)]
        self.assertTrue(8 <= len(silent) <= 16, len(silent))
        self.assertEqual(silent, [d for d in days if cards.silent_day(d)])


class GrownLines(unittest.TestCase):
    def test_valid_rejects_what_the_voice_rules_forbid(self):
        seen = {"the old line."}
        self.assertTrue(growth._valid("Every door is sealed.", "Good.", seen))
        self.assertFalse(growth._valid("The Old Line.", "Good.", seen))       # duplicate
        self.assertFalse(growth._valid("I am an AI.", "Good.", seen))         # tech word
        self.assertFalse(growth._valid("A pause — then nothing.", "Good.", seen))  # em dash
        self.assertFalse(growth._valid("x", "Good.", seen))                   # too short
        self.assertFalse(growth._valid("Bell\x07 rings.", "Good.", seen))     # control char


class GameLines(unittest.TestCase):
    def test_reactive_keys_are_lowercase_exe_names(self):
        for exe in games.REACTIVE:
            self.assertEqual(exe, exe.lower())
            self.assertTrue(exe.endswith(".exe"), exe)


if __name__ == "__main__":
    unittest.main()
