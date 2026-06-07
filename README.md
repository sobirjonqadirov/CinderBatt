# CinderBatt

A lightweight Windows app that protects your battery life by automatically enforcing power-saving rules the moment you unplug.

Built with Python + PyQt6. Free and open source.

---

## What it does

- Detects when your laptop unplugs and instantly switches into restriction mode
- Kills blacklisted apps (Steam, Discord, Wallpaper Engine, etc.) and their child processes
- Enforces rules continuously — if a blacklisted app reopens, it gets closed again
- When you plug back in, offers to restore everything that was closed
- Checks for updates on every launch
- Runs silently in the system tray

---

## Installation

1. Go to [Releases](https://github.com/sobirjonqadirov/CinderBatt/releases)
2. Download the latest `CinderBatt-alpha-x.x-setup.exe`
3. Run the installer and follow the steps
4. CinderBatt starts automatically and lives in your system tray

---

## Customizing the blacklist

After installation, open `blacklist.toml` in your install directory (default: `C:\Program Files\CinderBatt\`). It's a plain text file you can edit in Notepad:

```toml
[blacklist]
apps = [
    "steam.exe",
    "discord.exe",
    "your-app-here.exe",
]

[options]
# Set to false if you don't want child processes killed too
kill_process_tree = true
```

Restart CinderBatt after saving changes.

---

## Running from source

Requirements: Python 3.11+, Windows

```bash
git clone https://github.com/sobirjonqadirov/CinderBatt.git
cd CinderBatt
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python src/main.py
```

---

## Building

Requires [PyInstaller](https://pyinstaller.org) and [Inno Setup](https://jrsoftware.org/isinfo.php).

```bash
# Build the exe
pyinstaller build/app.spec --distpath server/releases --workpath build/work --clean

# Then open build/installer.iss in Inno Setup and compile
```

---

## Roadmap

| Version | Focus |
|---|---|
| Alpha 1.0 | Core — tray, dashboard, blacklist, restore, update checker |
| Alpha 1.1 | Activity log, per-app restore, Steam game relaunch fix |
| Alpha 1.2 | GPU switching (NVIDIA → Intel on battery) |
| Alpha 1.3 | Blacklist editor inside dashboard |
| Alpha 1.4 | Feedback system |
| Beta 1.0 | First public release |

---

## Contributing

Pull requests welcome. If you want to add a rule, open an issue first describing what it does and we'll figure out the best way to implement it.

---

## License

No license yet — free to use, not for redistribution or commercial use without permission.