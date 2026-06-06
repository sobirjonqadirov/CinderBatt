import tomllib
import os
from config import BASE_DIR, BLACKLIST_PATH

def load_blacklist() -> list[str]:
    try:
        with open(BLACKLIST_PATH, "rb") as f:
            data = tomllib.load(f)
        return [app.lower() for app in data["blacklist"]["apps"]]
    except FileNotFoundError:
        print("[blacklist] blacklist.toml not found, using empty list")
        return []
    except Exception as e:
        print(f"[blacklist] failed to load: {e}")
        return []