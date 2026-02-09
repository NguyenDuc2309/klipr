import datetime


def format_time(timestamp_str):
    """Format a UTC timestamp string to a human-readable relative time."""
    try:
        dt_utc = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        dt_utc = dt_utc.replace(tzinfo=datetime.timezone.utc)
        dt_local = dt_utc.astimezone()  # Convert to system local timezone

        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        diff = now - dt_local
        seconds = diff.total_seconds()

        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            return f"{int(seconds / 60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)}h ago"
        elif seconds < 604800:
            return f"{int(seconds / 86400)}d ago"
        else:
            return dt_local.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return timestamp_str
