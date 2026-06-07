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