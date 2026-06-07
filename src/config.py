# CinderBatt - A lightweight Windows battery management app
# Copyright (C) 2026 Sobirjon Qadirov
# Licensed under GNU GPL v3 — see LICENSE for details

import os
import sys

def _base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _bundled_file(filename: str) -> str:
    """For files bundled inside the exe via datas."""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(_base_dir(), filename)

def _assets_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets')
    return os.path.join(_base_dir(), 'assets')

APP_NAME    = "CinderBatt"
VERSION     = "alpha-1.0"
BASE_DIR    = _base_dir()
ASSETS_DIR  = _assets_dir()

ICON_TRAY       = os.path.join(ASSETS_DIR, "icon-transparent.png")
ICON_NORMAL     = os.path.join(ASSETS_DIR, "icon.png")
ICON_INVERSE    = os.path.join(ASSETS_DIR, "icon-inverse.png")

# bundled read-only files → _MEIPASS
BLACKLIST_PATH   = _bundled_file("blacklist.toml")

# user-generated files → next to the .exe
RULES_STATE_PATH = os.path.join(BASE_DIR, "rules.json")
RESTORE_PATH     = os.path.join(BASE_DIR, "session_restore.json")

UPDATE_SERVER_URL = "https://raw.githubusercontent.com/sobirjonqadirov/CinderBatt/main/server/version.json"