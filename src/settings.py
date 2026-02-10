import json
from pathlib import Path

LOCAL_SETTINGS = Path("setting.json")
USER_SETTINGS_DIR = Path.home() / ".config" / "klipr"
USER_SETTINGS_FILE = USER_SETTINGS_DIR / "setting.json"

DEFAULTS = {
    "name": "Klipr",
    "version": "0.2",
    "description": "Clipboard Manager",
    "closeToTray": True,
    "autostart": False,
    "theme": "dark",
    "shortcut": "<Alt>v",
    "shortcutEnabled": True,
    "historyLimit": 50,
}

_settings_cache = None


def _ensure_dir():
    """Ensure user settings directory exists."""
    USER_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)


def get_settings_file():
    """Return the path to the settings file to use."""
    if LOCAL_SETTINGS.exists():
        return LOCAL_SETTINGS
    return USER_SETTINGS_FILE


def reload():
    """Force reload settings from disk."""
    global _settings_cache
    _settings_cache = None
    return load()


def load():
    """Load settings from JSON file. Favor local setting.json if exists."""
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache

    settings_file = get_settings_file()

    if not settings_file.exists() and not LOCAL_SETTINGS.exists():
        _ensure_dir()
        settings_file = USER_SETTINGS_FILE
        try:
            with open(settings_file, "w") as f:
                json.dump(DEFAULTS, f, indent=4)
        except IOError:
            pass

    if settings_file.exists():
        try:
            with open(settings_file, "r") as f:
                user_settings = json.load(f)
                _settings_cache = {**DEFAULTS, **user_settings}
                return _settings_cache
        except (json.JSONDecodeError, IOError):
            pass

    _settings_cache = DEFAULTS.copy()
    return _settings_cache


def save(data=None):
    """Save settings to JSON file."""
    global _settings_cache
    
    if LOCAL_SETTINGS.exists():
        target_file = LOCAL_SETTINGS
    else:
        _ensure_dir()
        target_file = USER_SETTINGS_FILE

    if data is None:
        data = _settings_cache if _settings_cache is not None else DEFAULTS.copy()
    else:
        _settings_cache = data

    try:
        with open(target_file, "w") as f:
            json.dump(data, f, indent=4)
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
    
    target_file = get_settings_file()
    if target_file.exists():
        try:
            target_file.unlink()
        except OSError:
            pass
