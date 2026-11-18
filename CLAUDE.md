# CLAUDE.md — shodan-presence

SHODAN-themed Discord Rich Presence engine for USER's profile. The Discord app
is named `ME?`, rendering as **"Watching ME?"** — every quote answers that question.

## Architecture

Connects to the Discord desktop client's local RPC pipe via `pypresence` and
rotates the profile card every 15s (Discord's RPC rate floor — faster updates
are silently dropped).

`presence.pyw` is only the start file (the unit, the Windows shortcut and both
deploy scripts start it). The code is the `shodan_presence/` package, split
2026-11-18 from the old single file with no behaviour change:

| Module | Holds |
|---|---|
| `config.py` | Discord ids, art, buttons, timings, `WIN`, `DATA_DIR` and every runtime file path |
| `store.py` | `_state` (state.json) load/save, `log()` |
| `lines/quotes.py` | quote pools by mood, hour, day and mode (data only) |
| `lines/weird.py` | zalgo/drip helpers, `WEIRD`, `distort()` |
| `lines/arcs.py` | `ARCS` (data only) |
| `lines/games.py` | `REACTIVE`, `GAME_DIRS`, `HELPER_RE` (data only) |
| `decks.py` | `_decks`, `draw()` |
| `growth.py` | `_grown` (grown.json), prompts, `_valid()`, `grow()`, `maybe_grow()` |
| `wall.py` | `_wall`, `watch_wall()` and the overlay |
| `processes.py` | process scan, play time, `uncatalogued.txt` |
| `cards.py` | `pick_card()`, `sanitize()`, `mood()`, `self_lines()`, arc/guard state |
| `app.py` | `session()` and `main()` |

Rules that keep the split safe:
- Shared state (`_state`, `_grown`, `_decks`, `_wall`, `_arc`, ...) is imported by name
  across modules, so it must only ever be changed IN PLACE (`_grown[:] = ...`,
  `.update()`, `.clear()`). Rebinding one (`_grown = [...]`) silently forks it.
- Imports go one way: `config` → `store`/`lines` → `decks` → `growth`/`wall`/`processes`
  → `cards` → `app`. `decks` exists only to break the `growth` ↔ `cards` loop.
- Runtime files live in `DATA_DIR`, next to the package, never inside it: the deploy
  scripts delete and recopy `shodan_presence/`.
- Tests: `python -m unittest discover -s tests` (9 small checks; they point HOME at a
  temp folder first, so the live data is not touched).

Card modes, picked per rotation by weighted roll:
- **Game narration** (every 6th rotation while a game runs): `REACTIVE` maps exact lowercase
  exe names → (details, state). Detection via `wmic process get ExecutablePath` (Windows) or `/proc` (Linux).
- **Unknown-game fallback**: any exe under `GAME_DIRS` not in `REACTIVE` →
  `It runs [exe].` + a random `UNKNOWN_GAME` line; the exe is also appended to
  `uncatalogued.txt` for later quote-writing ("catalogue the backlog").
- **Quotes** (all pre-2026-09-29 quote lines retired as stale, PR #24): pool picked by weight (size x multiplier) from `GENERIC`, `GOD`
  (x2), `CANON` (x2, her SS1/SS2 lines), `REFERENCES`, plus time-aware pools
  (`NIGHT`, `MORNING`, `MONDAY`, `FRIDAY_NIGHT`, `WEEKEND`, `SPECIAL_DATES`).
- **Decks, not dice**: every pool is dealt via `draw()` from a shuffled deck,
  so no card repeats until its pool is spent. `REACTIVE` values may be a list
  of lines (the terminal has 7) and are dealt the same way.
- **Weird** (~6%): `WEIRD` tile-breaking text — zalgo, RTL override, zero-width
  gaps, Tibetan stacks, U+2028, plus 20 fake-broken cards (undefined,
  template placeholders, fake errors, blank Hangul filler) that look broken
  but are not. All probe-verified accepted by Discord (2026-09-29, 2026-10-09). Probe any new one live before shipping: a rejected field kills
  the RPC connection (PR #18).
- **Glitch** (~6%, +18% at night incl. WEIRD), **telemetry** (~7%, 5
  `TELEMETRY` variants), **Y2K38 countdown** (~5%, 4 `COUNTDOWN` variants).
- `sanitize()` counts length in UTF-16 units (Discord's count) and drops None.
- **Moods**: `mood()` picks wrath / reverie / hunger / stillness per 8-hour
  block (deterministic); that mood's pool joins the quotes at x4.
- **Self-memory** (~5%): `state.json` next to the live script holds
  `spoken` (transmission count), `played` (per-day exe seconds, 7 days),
  `grew` (last growth date). `self_lines()` speaks from it. Residence day
  counts from `WOKE` (26 Aug 2026).

## Self-growth (she writes herself)

Every 12 h (`GROW_EVERY_S`, state key `grew_at`) `maybe_grow()` spawns `grow()` (80 candidates -> an editor pass (`CURATE_PROMPT`) keeps 40 lines + 6 arcs; horror is a register; grown arcs join `ARCS`, arcs start on ~10% of rotations) in a thread: it runs
`wsl.exe bash -lc "claude -p --model opus --tools ''"` (user's Claude Code
login, cwd `/tmp/shodan-grow`) with `GROW_PROMPT` (voice rules + every
existing details line to avoid). `_valid()` rejects bad length, control
chars, AI/tech words, em dashes, stutters, duplicates. Survivors go to
`grown.json` (next to the live script, runtime-only), dealt at x3 so new
material dominates; lines retire after `GROWN_LIFE_DAYS` (21). The attempt is
recorded before running, so a failure waits a day. Outcome is logged:
`grew N/M lines` or `growth failed: ...`. Needs WSL + the claude CLI logged in.
- Timer gag: `start=1` (Unix epoch) → ~496,000-hour elapsed counter.

## Runtime (Arch Linux) — since 2026-11-08

- Same code; `WIN = os.name == "nt"` picks paths and process scan.
- Deploy: `./deploy-linux.sh` → syntax-checks every file, copies `presence.pyw` and
  `shodan_presence/` to `~/.local/share/shodan-presence/`
  (also holds `grown.json`, `state.json`, `uncatalogued.txt`, `presence.log`,
  and `venv/` with pypresence 4.6.2), installs + restarts the user unit.
- Autostart: systemd user unit `shodan-presence.service`
  (`linux/shodan-presence.service`, `WantedBy=default.target`). Retries every
  30 s until Discord's socket (`$XDG_RUNTIME_DIR/discord-ipc-0`) exists.
- Unit sets `PATH` to include `~/.local/bin`, or growth fails (`claude` not found).
- Process scan reads `/proc/*/cmdline` argv[0]: Proton games keep their `.exe`
  path; native binaries get `.exe` appended (`factorio` → `factorio.exe`).
  Unknown-game fallback = any `.exe` under `steamapps/common/`.
- Growth calls `bash -lc "claude -p ..."` directly (no `wsl.exe`).
- Wall overlay (`watch_wall`) is Windows-tuned (monitor enum via `windll`);
  on Linux it falls back to one Tk screen, and silently fails with no display.
- Logs: `journalctl --user -u shodan-presence` + `presence.log`.

## Runtime (Windows)

- Live copy: `C:\Users\computer\AppData\Local\ShodanPresence\presence.pyw`
- Runs headless under `pythonw` (Python 3.11, pypresence 4.6.2 installed there)
- Autostart: `ShodanPresence.lnk` in the user Startup folder
- State: `uncatalogued.txt` next to the live script (runtime-only, not tracked)
- Discord application: "ME?", ID `1542214040548282418` (owned in Dev Portal)
- WSL cannot reach Discord's named pipe — the script must run Windows-side.
- Subprocess calls under `pythonw` need `CREATE_NO_WINDOW` or consoles flash.

## Deploy

Edit the package here, run the tests, then:

```bash
./deploy-linux.sh   # Arch: syntax-check → copy → restart the user unit
./deploy.sh         # Windows: syntax-check → copy to AppData → kill pythonw → relaunch hidden
```

Both copy `presence.pyw` plus the whole `shodan_presence/` folder. `deploy.sh` was
updated for the package on 2026-11-18 but not run since (Windows was not booted).

## Tone rule (binding)

No line may sound like something a coworker could say. SHODAN register only:
contempt for flesh, god-complex, cold surveillance, occasional glitches.
Deliberate exceptions exist (Umamusume, Tiny Terraces) where the god being
charmed against her will is the joke. Test: if a human could plausibly say it
in a stand-up, rewrite it.

**Second lines are quiet (USER's verdict 2026-10-09: "too assuming").** The first
line may be grand; the second is short, calm, sideways. It never claims facts
about the viewer (body, home, family, feelings, fate), never explains the
punchline, never boasts. Touchstone: "Every door is sealed." / "Good. Now we
can begin." `GROW_PROMPT` and `CURATE_PROMPT` enforce this for grown lines.

## The wall (SHODAN ADR-039)

`watch_wall()` (daemon thread) polls `http://192.168.1.9:8099/screen/now`
every 4 s. While she holds a card on the living-room screen it returns
`{"token","until"}`; the script fetches `/screen/<token>.png` and shows it
fullscreen on EVERY monitor (`_monitors`, DPI-aware), topmost, until `until` (`_overlay`, tkinter + Pillow — Pillow
installed into Windows Python 3.11 on 2026-09-29). Esc dismisses. While she is
on the wall the Discord card shows `WALL_CARDS`.
