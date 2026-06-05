import os

APP_NAME    = "CinderBatt"
VERSION     = "alpha-1.0"
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
SERVER_PATH = os.path.join(BASE_DIR, "server", "version.json")

ICON_TRAY       = os.path.join(ASSETS_DIR, "icon-transparent.png")
ICON_NORMAL     = os.path.join(ASSETS_DIR, "icon.png")
ICON_INVERSE    = os.path.join(ASSETS_DIR, "icon-inverse.png")