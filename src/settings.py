import json
import os
from pathlib import Path

SETTINGS_DIR = Path.home() / ".config" / "klipr"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULTS = {
    "close_to_tray": True,
    "autostart": False,
    "theme": "dark",
    "shortcut": "<Ctrl><Shift>v",
    "shortcut_enabled": True,
}

_settings_cache = None


def _ensure_dir():
    """Ensure settings directory exists."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)


def load():
    """Load settings from JSON file, return dict with defaults merged."""
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache

    _ensure_dir()

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                user_settings = json.load(f)
                # Merge with defaults (user settings override defaults)
                _settings_cache = {**DEFAULTS, **user_settings}
                return _settings_cache
        except (json.JSONDecodeError, IOError):
            pass

    # Return defaults if file doesn't exist or is corrupted
    _settings_cache = DEFAULTS.copy()
    return _settings_cache


def save(data=None):
    """Save settings to JSON file. If data is None, saves current cache."""
    global _settings_cache
    _ensure_dir()

    if data is None:
        data = _settings_cache if _settings_cache is not None else DEFAULTS.copy()
    else:
        _settings_cache = data

    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error saving settings: {e}")


def get(key):
    """Get a setting value by key."""
    settings = load()
    return settings.get(key, DEFAULTS.get(key))


def set(key, value):
    """Set a setting value and save immediately."""
    settings = load()
    settings[key] = value
    save(settings)


def reset():
    """Reset settings to defaults."""
    global _settings_cache
    _settings_cache = None
    if SETTINGS_FILE.exists():
        SETTINGS_FILE.unlink()

