"""SHODAN Rich Presence engine. Start file: the code lives in shodan_presence/.

This file keeps its name and place because the systemd unit, the Windows shortcut and
both deploy scripts start it.
"""
from shodan_presence.app import main

if __name__ == "__main__":
    main()
