import json
import os
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtGui import QIcon
from config import VERSION, SERVER_PATH, ICON_NORMAL

def check_for_updates(app: QApplication) -> tuple[bool, str, bool, str]:
    try:
        if not os.path.exists(SERVER_PATH):
            return False, "", False, ""

        with open(SERVER_PATH, "r") as f:
            data = json.load(f)

        latest       = data.get("latest", "")
        url          = data.get("url", "")
        experimental = data.get("experimental", False)
        exp_note     = data.get("experimental_note", "")

        if latest != VERSION:
            return True, url, experimental, exp_note

        return False, "", False, ""

    except Exception as e:
        print(f"[updater] failed to check: {e}")
        return False, "", False, ""


def prompt_update(latest_url: str, experimental: bool, exp_note: str) -> bool:
    msg = QMessageBox()
    msg.setWindowTitle("Update Available")
    msg.setWindowIcon(QIcon(ICON_NORMAL))

    if experimental:
        msg.setIcon(QMessageBox.Icon.Warning)
        note_line = f"\n⚠ Experimental build — {exp_note}\nThese builds may be unstable or incomplete.\n"
    else:
        msg.setIcon(QMessageBox.Icon.Information)
        note_line = ""

    msg.setText(
        f"A new version of CinderBatt is available.\n\n"
        f"Current version : {VERSION}\n"
        f"{note_line}\n"
        f"Download now?"
    )
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)

    result = msg.exec()
    return result == QMessageBox.StandardButton.Yes


def apply_update(url: str):
    try:
        if os.path.exists(url):
            import subprocess, sys
            subprocess.Popen([url])
            sys.exit()
        else:
            print(f"[updater] release not found at: {url}")
    except Exception as e:
        print(f"[updater] failed to apply update: {e}")