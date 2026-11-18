#!/usr/bin/env bash
# Arch/Linux: install presence.pyw + systemd user service, (re)start it.
set -euo pipefail
cd "$(dirname "$0")"
T="$HOME/.local/share/shodan-presence"
mkdir -p "$T" "$HOME/.config/systemd/user"
[ -x "$T/venv/bin/python" ] || { python3 -m venv "$T/venv" && "$T/venv/bin/pip" -q install pypresence==4.6.2; }
"$T/venv/bin/python" -c "import ast,sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())" presence.pyw
cp presence.pyw "$T/presence.pyw"
cp linux/shodan-presence.service "$HOME/.config/systemd/user/"
systemctl --user daemon-reload
systemctl --user enable --now shodan-presence.service
systemctl --user restart shodan-presence.service
sleep 5
systemctl --user is-active shodan-presence.service && tail -3 "$T/presence.log"
