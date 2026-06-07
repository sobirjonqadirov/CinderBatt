# CinderBatt - A lightweight Windows battery management app
# Copyright (C) 2026 Sobirjon Qadirov
# Licensed under GNU GPL v3 — see LICENSE for details

import tomllib
import os
from config import BASE_DIR, BLACKLIST_PATH

def load_blacklist() -> tuple[list[str], bool]:
    try:
        with open(BLACKLIST_PATH, "rb") as f:
            data = tomllib.load(f)
        apps             = [app.lower() for app in data["blacklist"]["apps"]]
        kill_tree        = data.get("options", {}).get("kill_process_tree", True)
        return apps, kill_tree
    except FileNotFoundError:
        print("[blacklist] blacklist.toml not found, using empty list")
        return [], True
    except Exception as e:
        print(f"[blacklist] failed to load: {e}")
        return [], True