import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame,
    QSystemTrayIcon, QMenu, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
from config import (
    APP_NAME, VERSION,
    ICON_TRAY, ICON_NORMAL, ICON_INVERSE
)

class TrayIcon(QSystemTrayIcon):
    def __init__(self, app: QApplication, dashboard: "Dashboard"):
        super().__init__(QIcon(ICON_TRAY), app)
        self.dashboard = dashboard
        self.setToolTip(f"{APP_NAME} {VERSION}")
        self._build_menu()

    def _build_menu(self):
        menu = QMenu()

        open_action = QAction("Open Dashboard", self.dashboard)
        open_action.triggered.connect(self.dashboard.show_and_raise)
        menu.addAction(open_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self.dashboard)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.dashboard.show_and_raise()

class RestorePopup(QWidget):
    def __init__(self, snapshot: list, parent=None):
        super().__init__(parent)
        self.snapshot = snapshot
        self.setWindowTitle("Restore Apps")
        self.setWindowIcon(QIcon(ICON_NORMAL))
        self.setMinimumSize(340, 250)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1f;
                color: #c8c8d8;
            }
            QLabel#title {
                font-size: 14px;
                font-weight: 500;
                color: #e8e8f0;
            }
            QCheckBox {
                font-size: 12px;
                color: #c8c8d8;
                padding: 4px 0;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #3a3a48;
                border-radius: 3px;
                background: #2a2a35;
            }
            QCheckBox::indicator:checked {
                background: #ff6b35;
                border-color: #ff6b35;
            }
            QPushButton {
                background-color: #2a2a35;
                color: #c8c8d8;
                border: 1px solid #3a3a48;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #32323f; }
            QPushButton#restore-btn {
                background-color: #ff6b35;
                color: #fff;
                border: none;
            }
            QPushButton#restore-btn:hover { background-color: #e55a25; }
        """)
        self._build_ui()
        self.adjustSize()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Restore closed apps?")
        title.setObjectName("title")
        layout.addWidget(title)

        sub = QLabel("These apps were closed when you unplugged.")
        sub.setStyleSheet("font-size: 11px; color: #555;")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        self.checkboxes = []
        self.entries    = []
        for entry in self.snapshot:
            cb = QCheckBox(entry["name"])
            cb.setChecked(True)
            self.checkboxes.append(cb)
            self.entries.append(entry)
            layout.addWidget(cb)

        layout.addStretch()

        btn_row = QHBoxLayout()
        restore_btn = QPushButton("Restore Selected")
        restore_btn.setObjectName("restore-btn")
        restore_btn.clicked.connect(self._restore_selected)
        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.clicked.connect(self._dismiss)
        btn_row.addWidget(restore_btn)
        btn_row.addWidget(dismiss_btn)
        layout.addLayout(btn_row)

    def _restore_selected(self):
        from rules import BlacklistRule
        selected = [
            entry for cb, entry
            in zip(self.checkboxes, self.entries)
            if cb.isChecked()
        ]
        BlacklistRule.restore_apps(selected)
        BlacklistRule.clear_restore_snapshot()
        self.close()

    def _dismiss(self):
        from rules import BlacklistRule
        BlacklistRule.clear_restore_snapshot()
        self.close()

class Dashboard(QMainWindow):
    def __init__(self, power_monitor):
        super().__init__()
        self.power_monitor = power_monitor
        self.restricted    = False
        self.update_info   = None
        from rule_engine import RuleEngine
        self.engine = RuleEngine()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(ICON_NORMAL))
        self.setFixedSize(440, 520)
        self.setWindowFlags(Qt.WindowType.Window)

        self._apply_theme()
        self._build_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh_status)
        self.timer.start(5000)

        self.enforce_timer = QTimer()
        self.enforce_timer.timeout.connect(self._enforce_rules)
        self.enforce_timer.setInterval(3000)

    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1f;
            }
            QWidget#central {
                background-color: #1a1a1f;
            }
            QLabel#title {
                font-size: 18px;
                font-weight: 500;
                color: #e8e8f0;
            }
            QLabel#version {
                font-size: 11px;
                color: #444;
            }
            QLabel#section {
                font-size: 11px;
                color: #555;
                letter-spacing: 1px;
            }
            QLabel#status-key {
                font-size: 12px;
                color: #666;
            }
            QLabel#status-val {
                font-size: 12px;
                font-weight: 500;
                color: #c8c8d8;
            }
            QFrame#status-card {
                background-color: #111116;
                border: 1px solid #2e2e38;
                border-radius: 10px;
            }
            QFrame#divider {
                background-color: #2e2e38;
            }
            QPushButton#toggle-btn {
                background-color: #2a2a35;
                color: #c8c8d8;
                border: 1px solid #3a3a48;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton#toggle-btn:hover {
                background-color: #32323f;
                border-color: #ff6b35;
            }
            QPushButton#toggle-btn:pressed {
                background-color: #ff6b35;
                color: #fff;
            }
            QFrame#update-banner {
                background-color: #1e2a1e;
                border: 1px solid #2d4a2d;
                border-radius: 8px;
            }
            QLabel#update-text {
                font-size: 12px;
                color: #6dbf6d;
            }
            QPushButton#update-btn {
                background-color: #2d5a2d;
                color: #6dbf6d;
                border: none;
                border-radius: 5px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton#update-btn:hover {
                background-color: #3a7a3a;
            }
            QPushButton#dismiss-btn {
                background-color: transparent;
                color: #555;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 4px 10px;
                font-size: 11px;
            }
            QPushButton#dismiss-btn:hover {
                color: #888;
            }
        """)

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # --- header ---
        header = QHBoxLayout()
        title  = QLabel(APP_NAME)
        title.setObjectName("title")
        ver    = QLabel(VERSION)
        ver.setObjectName("version")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(ver)
        layout.addLayout(header)

        # --- update banner (hidden by default) ---
        self.update_banner = QFrame()
        self.update_banner.setObjectName("update-banner")
        self.update_banner.setVisible(False)
        banner_layout = QHBoxLayout(self.update_banner)
        banner_layout.setContentsMargins(12, 8, 12, 8)
        self.update_label = QLabel("Update available")
        self.update_label.setObjectName("update-text")
        dl_btn = QPushButton("Download")
        dl_btn.setObjectName("update-btn")
        dl_btn.setFixedWidth(80)
        dl_btn.clicked.connect(self._on_download)
        dismiss_btn = QPushButton("Dismiss")
        dismiss_btn.setObjectName("dismiss-btn")
        dismiss_btn.setFixedWidth(64)
        dismiss_btn.clicked.connect(lambda: self.update_banner.setVisible(False))
        banner_layout.addWidget(self.update_label)
        banner_layout.addStretch()
        banner_layout.addWidget(dl_btn)
        banner_layout.addWidget(dismiss_btn)
        layout.addWidget(self.update_banner)

        # --- status card ---
        status_card = QFrame()
        status_card.setObjectName("status-card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(16, 14, 16, 14)
        status_layout.setSpacing(10)

        power_row = QHBoxLayout()
        power_key = QLabel("POWER")
        power_key.setObjectName("status-key")
        self.power_val = QLabel("Checking...")
        self.power_val.setObjectName("status-val")
        power_row.addWidget(power_key)
        power_row.addStretch()
        power_row.addWidget(self.power_val)
        status_layout.addLayout(power_row)

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        status_layout.addWidget(divider)

        mode_row = QHBoxLayout()
        mode_key = QLabel("MODE")
        mode_key.setObjectName("status-key")
        self.mode_val = QLabel("Unrestricted")
        self.mode_val.setObjectName("status-val")
        self.mode_val.setStyleSheet("color: #4caf6e;")
        mode_row.addWidget(mode_key)
        mode_row.addStretch()
        mode_row.addWidget(self.mode_val)
        status_layout.addLayout(mode_row)

        layout.addWidget(status_card)

        # --- rules section (dynamic) ---
        rules_label = QLabel("RULES")
        rules_label.setObjectName("section")
        layout.addWidget(rules_label)

        for rule in self.engine.get_rules():
            rule_frame = QFrame()
            rule_frame.setObjectName("status-card")
            rule_layout = QHBoxLayout(rule_frame)
            rule_layout.setContentsMargins(16, 12, 16, 12)
            rule_name_lbl = QLabel(rule.name)
            rule_name_lbl.setObjectName("status-val")
            rule_desc_lbl = QLabel(rule.description)
            rule_desc_lbl.setObjectName("status-key")
            rule_text = QVBoxLayout()
            rule_text.addWidget(rule_name_lbl)
            rule_text.addWidget(rule_desc_lbl)
            rule_layout.addLayout(rule_text)
            rule_layout.addStretch()
            layout.addWidget(rule_frame)

        layout.addStretch()

        # --- toggle button ---
        self.toggle_btn = QPushButton("Enable Restriction Mode")
        self.toggle_btn.setObjectName("toggle-btn")
        self.toggle_btn.setFixedHeight(42)
        self.toggle_btn.clicked.connect(self._toggle_restriction)
        layout.addWidget(self.toggle_btn)

    def show_update_banner(self, url: str, experimental: bool, exp_note: str):
        self.update_info = (url, experimental, exp_note)
        text = "⚠ Experimental update available" if experimental else "Update available"
        self.update_label.setText(text)
        self.update_banner.setVisible(True)

    def _on_download(self):
        if self.update_info:
            from updater import apply_update
            apply_update(self.update_info[0])

    def _toggle_restriction(self):
        if self.restricted:
            self._remove_restrictions()
        else:
            self._apply_restrictions()

    def _apply_restrictions(self):
        self.restricted = True
        self._refresh_status()
        self.engine.apply_all()
        self.enforce_timer.start()

    def _remove_restrictions(self):
        self.restricted = False
        self.enforce_timer.stop()
        self.engine.revert_all()
        self._refresh_status()
        self._show_restore_popup()

    def _enforce_rules(self):
        if not self.restricted:
            return
        self.engine.enforce_all()

    def _show_restore_popup(self):
        from rules import BlacklistRule
        snapshot = BlacklistRule.load_restore_snapshot()
        if not snapshot:
            return
        self.restore_popup = RestorePopup(snapshot, parent=None)
        self.restore_popup.show()

    def _refresh_status(self):
        charging = self.power_monitor.is_charging()

        # handle None (API read failure)
        if charging is None:
            self.power_val.setText("Unknown")
            self.power_val.setStyleSheet("color: #666;")
        elif charging:
            self.power_val.setText("Charging")
            self.power_val.setStyleSheet("color: #4caf6e;")
        else:
            self.power_val.setText("On Battery")
            self.power_val.setStyleSheet("color: #e07b39;")

        if self.restricted:
            self.mode_val.setText("Restricted")
            self.mode_val.setStyleSheet("color: #e07b39;")
            self.toggle_btn.setText("Disable Restriction Mode")
            self.toggle_btn.setStyleSheet(
                "QPushButton#toggle-btn {"
                "background-color: #3a1f1a;"
                "color: #e07b39;"
                "border: 1px solid #5a3020;"
                "border-radius: 8px;"
                "padding: 10px;"
                "font-size: 13px;"
                "font-weight: 500;}"
            )
        else:
            self.mode_val.setText("Unrestricted")
            self.mode_val.setStyleSheet("color: #4caf6e;")
            self.toggle_btn.setText("Enable Restriction Mode")
            self.toggle_btn.setStyleSheet("")

    def show_and_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()