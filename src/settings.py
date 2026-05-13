import json
from pathlib import Path

LOCAL_SETTINGS = Path("setting.json")
USER_SETTINGS_DIR = Path.home() / ".config" / "klipr"
USER_SETTINGS_FILE = USER_SETTINGS_DIR / "setting.json"

_settings_cache = None


def _ensure_dir():
    """Ensure user settings directory exists."""
    USER_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)



def _use_local_settings():
    return (
        LOCAL_SETTINGS.exists()
        and (Path.cwd() / "src").is_dir()
        and (Path.cwd() / "requirements.txt").exists()
    )


def get_base_settings_file():
    if _use_local_settings():
        return LOCAL_SETTINGS

    candidates = [
        Path(__file__).resolve().parent / "setting.json",
        Path(__file__).resolve().parent.parent / "setting.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def get_settings_file():
    """Return the path to the user settings file."""
    if _use_local_settings():
        return LOCAL_SETTINGS
    return USER_SETTINGS_FILE


def load_base_defaults():
    """Load base default settings from the bundled setting.json without user overrides.

    This is the single source of truth for default values; if the file is missing
    or invalid, we raise so bugs are visible instead of silently guessing.
    """
    base_file = get_base_settings_file()
    if not base_file:
        raise RuntimeError("Base settings file 'setting.json' not found")
    try:
        with open(base_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"Failed to load base settings from {base_file}: {e}")


def reload():
    """Force reload settings from disk."""
    global _settings_cache
    _settings_cache = None
    return load()


def load():
    """Load settings. Priority: User Config > Base Config (setting.json).

    Base config (setting.json) is required and is the only place where defaults
    are defined.
    """
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache

    # 1. Load Base Config (required setting.json)
    base_file = get_base_settings_file()
    if not base_file:
        raise RuntimeError("Base settings file 'setting.json' not found")
    try:
        with open(base_file, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"Failed to load base settings from {base_file}: {e}")

    if _use_local_settings():
        _settings_cache = config
        return _settings_cache

    # 2. Load User Config (~/.config/klipr/setting.json)
    user_file = USER_SETTINGS_FILE
    if not user_file.exists():
        _ensure_dir()
        # Init user config from current base config
        try:
            with open(user_file, "w") as f:
                json.dump(config, f, indent=4)
        except IOError:
            pass
    else:
        try:
            with open(user_file, "r") as f:
                user_config = json.load(f)
                config.update(user_config)
        except (json.JSONDecodeError, IOError):
            pass

    _settings_cache = config
    return _settings_cache


def save(data=None):
    """Save settings to JSON file."""
    global _settings_cache
    
    target_file = get_settings_file()
    if target_file == USER_SETTINGS_FILE:
        _ensure_dir()

    if data is None:
        if _settings_cache is None:
            # Ensure we always persist a concrete state derived from files,
            # never from hardcoded defaults.
            data = load()
        else:
            data = _settings_cache
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
    # Do not inject hidden defaults here; if a key is missing from config,
    # that's a bug in the JSON and should be fixed there.
    return settings[key]


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
