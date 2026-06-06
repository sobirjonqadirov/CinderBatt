import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from config import APP_NAME, ICON_NORMAL
from power import PowerMonitor
from updater import check_for_updates, prompt_update, apply_update
from ui import Dashboard, TrayIcon
import ctypes


def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_NAME)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(QIcon(ICON_NORMAL))

    # keep app running even when all windows are closed
    app.setQuitOnLastWindowClosed(False)

    # power monitor
    monitor = PowerMonitor()

    # dashboard
    dashboard = Dashboard(monitor)

    # tray icon
    tray = TrayIcon(app, dashboard)
    tray.show()

    # wire power events to dashboard
    monitor.unplugged.connect(dashboard._apply_restrictions)
    monitor.plugged.connect(dashboard._remove_restrictions)

    # clean shutdown
    app.aboutToQuit.connect(monitor.stop)

    # start power monitor thread
    monitor.start()

    # check for updates
    found, url, experimental, exp_note = check_for_updates(app)
    if found:
        if experimental:
            # always prompt for experimental
            if prompt_update(url, experimental, exp_note):
                apply_update(url)
        else:
            # show banner inside dashboard for stable updates
            dashboard.show_update_banner(url, experimental, exp_note)

    # show dashboard on first launch
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()