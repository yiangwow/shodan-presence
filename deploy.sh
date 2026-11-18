#!/usr/bin/env bash
# Deploy presence.pyw + the shodan_presence package to the Windows runtime dir and restart it.
set -euo pipefail
cd "$(dirname "$0")"

PY="/mnt/c/Users/computer/AppData/Local/Programs/Python/Python311/python.exe"
DEST="/mnt/c/Users/computer/AppData/Local/ShodanPresence"
WINPATH='C:\Users\computer\AppData\Local\ShodanPresence\presence.pyw'

# Syntax-check every file before anything is copied.
find presence.pyw shodan_presence -name '*.py*' -not -path '*/__pycache__/*' -print0 \
  | xargs -0 "$PY" -c "import ast,sys; [ast.parse(open(p, encoding='utf-8').read(), p) for p in sys.argv[1:]]"
cp presence.pyw "$DEST/presence.pyw"
rm -rf "$DEST/shodan_presence"   # no stale modules; runtime files live next to it, not inside
cp -r shodan_presence "$DEST/shodan_presence"
taskkill.exe /IM pythonw.exe /F 2>/dev/null || true
powershell.exe -NoProfile -Command "Start-Process -WindowStyle Hidden 'C:\\Users\\computer\\AppData\\Local\\Programs\\Python\\Python311\\pythonw.exe' -ArgumentList '\"$WINPATH\"'"
sleep 3
tasklist.exe | grep -i pythonw && echo "deployed + running"
