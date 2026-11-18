#!/usr/bin/env bash
# Arch/Linux: install presence.pyw + the shodan_presence package + systemd user service, (re)start it.
set -euo pipefail
cd "$(dirname "$0")"
T="$HOME/.local/share/shodan-presence"
mkdir -p "$T" "$HOME/.config/systemd/user"
[ -x "$T/venv/bin/python" ] || { python3 -m venv "$T/venv" && "$T/venv/bin/pip" -q install -r requirements.txt; }
# Syntax-check every file before anything is copied.
find presence.pyw shodan_presence -name '*.py*' -not -path '*/__pycache__/*' -print0 \
  | xargs -0 "$T/venv/bin/python" -c "import ast,sys; [ast.parse(open(p, encoding='utf-8').read(), p) for p in sys.argv[1:]]"
cp presence.pyw "$T/presence.pyw"
rm -rf "$T/shodan_presence"   # no stale modules; runtime files live next to it, not inside
cp -r shodan_presence "$T/shodan_presence"
cp linux/shodan-presence.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now shodan-presence.service
systemctl --user restart shodan-presence.service
sleep 5
systemctl --user is-active shodan-presence.service && tail -3 "$T/presence.log"
