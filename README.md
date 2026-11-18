# shodan-presence

A Discord Rich Presence card that behaves like SHODAN is living in your profile.

The Discord app is named `ME?`, so the profile reads **"Watching ME?"**. Every line on
the card answers that question. The card changes every 15 seconds.

## What it does

- Deals quotes from shuffled decks, so nothing repeats until a pool is spent.
- Changes with the hour, the weekday, a few dates, and her mood.
- Comments on the game or tool that is running.
- Plays short story arcs over several rotations.
- Sometimes glitches: zalgo, reversed text, cards that look broken but are not.
- Writes new lines for herself twice a day through the `claude` CLI, and retires them
  after three weeks.

## Layout

```
presence.pyw           start file
shodan_presence/
  config.py            ids, art, timings, file paths
  store.py             saved state and log
  lines/               everything she can say
  decks.py             shuffled decks
  growth.py            self-written lines
  wall.py              fullscreen card overlay
  processes.py         finds running games
  cards.py             picks and cleans the card
  app.py               Discord session and main loop
tests/                 small checks
```

## Run

Needs Python 3.11+ and the Discord desktop client running.

```bash
pip install -r requirements.txt
python presence.pyw
```

To use your own Discord application, change `CLIENT_ID` in `shodan_presence/config.py`.

Linux, as a systemd user service: `./deploy-linux.sh`

## Tests

```bash
python -m unittest discover -s tests
```
