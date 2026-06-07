# CinderBatt - A lightweight Windows battery management app
# Copyright (C) 2026 Sobirjon Qadirov
# Licensed under GNU GPL v3 — see LICENSE for details

import json
import requests
import tempfile
import subprocess
import sys
from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtGui import QIcon
from config import VERSION, UPDATE_SERVER_URL, ICON_NORMAL


def check_for_updates(app: QApplication) -> tuple[bool, str, bool, str]:
    try:
        response = requests.get(UPDATE_SERVER_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        latest       = data.get("latest", "")
        url          = data.get("url", "")
        experimental = data.get("experimental", False)
        exp_note     = data.get("experimental_note", "")

        if latest != VERSION:
            return True, url, experimental, exp_note

        return False, "", False, ""

    except requests.exceptions.ConnectionError:
        print("[updater] no internet connection, skipping update check")
        return False, "", False, ""
    except requests.exceptions.Timeout:
        print("[updater] update check timed out")
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
        print(f"[updater] downloading from {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)
            tmp_path = tmp.name

        print(f"[updater] launching {tmp_path}")
        subprocess.Popen([tmp_path])
        sys.exit()

    except Exception as e:
        print(f"[updater] update failed: {e}")