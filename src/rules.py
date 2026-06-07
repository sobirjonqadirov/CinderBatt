import psutil
import os
import json
import subprocess
from datetime import datetime
from blacklist import load_blacklist
from config import BASE_DIR, RESTORE_PATH

class BaseRule:
    name        : str = ""
    description : str = ""
    enabled     : bool = True

    def apply(self):   pass
    def enforce(self): pass
    def revert(self):  pass


class BlacklistRule(BaseRule):
    name        = "Blacklist Enforcer"
    description = "Kills blacklisted apps when restricted, restores on replug"
    enabled     = True

    def __init__(self):
        self._blacklist = load_blacklist()

    def apply(self):
        killed = {}  # path → entry, deduplicates by exe path

        for proc in psutil.process_iter(["name", "exe"]):
            try:
                proc_name = proc.info["name"]
                exe_path  = proc.info["exe"]
                if not proc_name or not exe_path:
                    continue
                if proc_name.lower() in self._blacklist:
                    proc.kill()
                    print(f"[blacklist] killed {proc_name}")
                    if exe_path not in killed:       # only store first instance
                        killed[exe_path] = {
                            "name":      proc_name,
                            "path":      exe_path,
                            "timestamp": datetime.now().isoformat()
                        }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if killed:
            self._save_restore_snapshot(list(killed.values()))

    def enforce(self):
        for proc in psutil.process_iter(["name"]):
            try:
                if not proc.info["name"]:
                    continue
                if proc.info["name"].lower() in self._blacklist:
                    proc.kill()
                    print(f"[blacklist] enforced: killed {proc.info['name']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def revert(self):
        pass  # revert is handled by RestorePrompt in ui, not here

    def _save_restore_snapshot(self, killed: list):
        try:
            with open(RESTORE_PATH, "w") as f:
                json.dump({"killed": killed}, f, indent=2)
        except Exception as e:
            print(f"[blacklist] failed to save restore snapshot: {e}")

    @staticmethod
    def load_restore_snapshot() -> list:
        try:
            if not os.path.exists(RESTORE_PATH):
                return []
            with open(RESTORE_PATH, "r") as f:
                data = json.load(f)
            return data.get("killed", [])
        except Exception as e:
            print(f"[blacklist] failed to load snapshot: {e}")
            return []

    @staticmethod
    def clear_restore_snapshot():
        try:
            if os.path.exists(RESTORE_PATH):
                os.remove(RESTORE_PATH)
        except Exception as e:
            print(f"[blacklist] failed to clear snapshot: {e}")

    @staticmethod
    def restore_apps(selected: list[dict]):
        for entry in selected:
            path = entry.get("path")
            name = entry.get("name", "unknown")
            if path and os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    print(f"[blacklist] restored {name}")
                except Exception as e:
                    print(f"[blacklist] failed to restore {name}: {e}")
            else:
                print(f"[blacklist] path not found for {name}: {path}")