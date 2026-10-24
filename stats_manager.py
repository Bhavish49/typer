"""
Stats Manager for Terminal Speed Typing Test.
Supports:
- Multi-user profiles with simple salted password hashing
- Per-user statistics, personal bests, and session history
- Demo / Guest mode (no stats saved)
- Weak Keys / Stumble Analysis (tracks characters with the most typing errors)
- ASCII trend charts, rolling averages (Ao5, Ao10), and CLI summaries
"""

import json
import os
import sys
import hashlib
import secrets
from datetime import datetime
from pathlib import Path


def get_history_file_path() -> Path:
    """
    Returns the path to the history file.
    Prefers user's home directory (~/.typer_history.json) so progress persists
    across any folder or global CLI invocation. Falls back to local directory.
    """
    try:
        home_path = Path.home() / ".typer_history.json"
        typen_path = Path.home() / ".typen_history.json"

        # Migrate if typen history exists and typer does not
        if not home_path.exists() and typen_path.exists():
            try:
                home_path.write_text(typen_path.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass

        if not home_path.exists():
            home_path.touch(exist_ok=True)
        return home_path
    except Exception:
        return Path(__file__).resolve().parent / "typing_history.json"


HISTORY_FILE = get_history_file_path()

# In-memory session state
_CURRENT_USER: str | None = None  # None = not chosen, "__demo__" = guest mode


def is_demo_mode() -> bool:
    """Returns True if the current session is in demo/guest mode."""
    return _CURRENT_USER is None or _CURRENT_USER == "__demo__"


def get_active_user() -> str | None:
    """Returns the username of the active profile, or None if in demo mode."""
    if _CURRENT_USER == "__demo__":
        return None
    return _CURRENT_USER


def set_active_user(username: str | None):
    """Sets the currently active user profile."""
    global _CURRENT_USER
    _CURRENT_USER = username


def set_demo_mode():
    """Activates Demo/Guest mode where no statistics are saved."""
    global _CURRENT_USER
    _CURRENT_USER = "__demo__"


def _hash_password(password: str, salt: str) -> str:
    """Generates a secure SHA-256 hash using the provided salt."""
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()


def _get_default_user_data(username: str = "guest") -> dict:
    """Default structure for a single user's stats."""
    return {
        "username": username,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "total_tests": 0,
            "total_time_seconds": 0.0,
            "total_words": 0,
            "best_wpm": 0,
            "best_accuracy": 0.0,
        },
        "records": {},  # key: f"{diff}_{length}", value: {"wpm": ..., "accuracy": ..., "date": ...}
        "sessions": [],  # list of session dicts
        "weak_keys": {},  # key: char, value: error_count
    }


def _load_raw_data() -> dict:
    """Loads raw JSON structure from disk, migrating legacy single-user data if needed."""
    if not HISTORY_FILE.exists():
        return {"version": 2, "users": {}}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"version": 2, "users": {}}

            # If this is a legacy v1 file without a 'users' dictionary, wrap it
            if "users" not in data:
                legacy_summary = data.get("summary", {})
                legacy_records = data.get("records", {})
                legacy_sessions = data.get("sessions", [])

                migrated = {
                    "version": 2,
                    "users": {},
                    "_legacy_data": {
                        "summary": legacy_summary,
                        "records": legacy_records,
                        "sessions": legacy_sessions,
                        "weak_keys": {},
                    }
                }
                return migrated
            return data
    except Exception:
        return {"version": 2, "users": {}}


def _save_raw_data(data: dict) -> bool:
    """Saves raw dictionary to the history file safely."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Failed to save typing history: {e}", file=sys.stderr)
        return False


def list_users() -> list[str]:
    """Returns a list of all registered profile usernames."""
    data = _load_raw_data()
    users = data.get("users", {})
    return sorted([info.get("username", k) for k, info in users.items()])


def user_exists(username: str) -> bool:
    """Checks if a user profile exists (case-insensitive)."""
    if not username:
        return False
    data = _load_raw_data()
    return username.lower().strip() in data.get("users", {})


def create_user(username: str, password: str) -> tuple[bool, str]:
    """
    Creates a new user profile with password authentication.
    Returns (success, message).
    """
    clean_username = username.strip()
    if len(clean_username) < 2:
        return False, "Username must be at least 2 characters long."
    if len(clean_username) > 20:
        return False, "Username must be 20 characters or fewer."
    if not clean_username.replace("_", "").isalnum():
        return False, "Username can only contain letters, numbers, and underscores."
    if clean_username.lower() in ("demo", "guest", "__demo__"):
        return False, "Username 'demo' and 'guest' are reserved for Demo Mode."

    data = _load_raw_data()
    users = data.setdefault("users", {})
    key = clean_username.lower()

    if key in users:
        return False, f"Username '{clean_username}' already exists. Please log in."

    salt = secrets.token_hex(8)
    password_hash = _hash_password(password, salt)

    user_data = _get_default_user_data(clean_username)
    user_data["salt"] = salt
    user_data["password_hash"] = password_hash

    # If there is legacy unassigned data and this is the first user, adopt it!
    if "_legacy_data" in data and len(users) == 0:
        legacy = data.pop("_legacy_data")
        user_data["summary"] = legacy.get("summary", user_data["summary"])
        user_data["records"] = legacy.get("records", user_data["records"])
        user_data["sessions"] = legacy.get("sessions", user_data["sessions"])
        user_data["weak_keys"] = legacy.get("weak_keys", {})

    users[key] = user_data
    data["last_user"] = clean_username
    _save_raw_data(data)

    set_active_user(clean_username)
    return True, f"Profile '{clean_username}' created successfully!"


def authenticate(username: str, password: str) -> tuple[bool, str]:
    """
    Verifies user credentials.
    Returns (success, message).
    """
    clean_username = username.strip()
    key = clean_username.lower()
    data = _load_raw_data()
    users = data.get("users", {})

    if key not in users:
        return False, f"User '{clean_username}' not found. Please create a profile first."

    user_info = users[key]
    salt = user_info.get("salt", "")
    expected_hash = user_info.get("password_hash", "")

    if _hash_password(password, salt) != expected_hash:
        return False, "Incorrect password. Please try again."

    set_active_user(user_info.get("username", clean_username))
    data["last_user"] = user_info.get("username", clean_username)
    _save_raw_data(data)
    return True, f"Welcome back, {user_info.get('username', clean_username)}!"


def get_last_active_user() -> str | None:
    """Returns the username of the user who logged in most recently."""
    data = _load_raw_data()
    return data.get("last_user")


def load_history(username: str | None = None) -> dict:
    """
    Loads history for the specified user or active user.
    If in Demo mode, returns an empty default structure (read-only in memory).
    """
    target = username or get_active_user()
    if target is None:
        return _get_default_user_data("Demo")

    data = _load_raw_data()
    users = data.get("users", {})
    user_data = users.get(target.lower())
    if user_data:
        return user_data
    return _get_default_user_data(target)


def save_user_history(user_data: dict, username: str | None = None) -> bool:
    """Saves updated user stats into the users database."""
    target = username or get_active_user()
    if target is None:
        # Demo mode does not persist data
        return True

    data = _load_raw_data()
    users = data.setdefault("users", {})
    users[target.lower()] = user_data
    return _save_raw_data(data)


def format_key_name(char: str) -> str:
    """Returns a readable label for a key (e.g. Space -> [SPACE])."""
    if char == " ":
        return "[SPACE]"
    elif char == "\t":
        return "[TAB]"
    elif char == "\n":
        return "[ENTER]"
    return f"'{char}'"


def get_top_weak_keys(username: str | None = None, top_n: int = 5) -> list[tuple[str, int]]:
    """
    Returns the top N keys with the highest error counts for the user:
    e.g. [('r', 14), ('b', 11), ('p', 8), ...]
    """
    data = load_history(username)
    weak_keys = data.get("weak_keys", {})
    if not weak_keys:
        return []

    sorted_keys = sorted(weak_keys.items(), key=lambda item: item[1], reverse=True)
    return sorted_keys[:top_n]


def record_session(
    diff_key: str,
    diff_name: str,
    length_key: str,
    length_name: str,
    wpm: int,
    accuracy: float,
    elapsed: float,
    total_chars: int,
    errors: int,
    errors_by_char: dict[str, int] | None = None,
) -> dict:
    """
    Records a completed typing session, updates personal bests and weak keys.
    In Demo mode, calculates metrics but does NOT write to disk!
    """
    # Demo Mode: transient in-memory calculations only
    if is_demo_mode():
        return {
            "is_category_pb": False,
            "is_overall_pb": False,
            "prev_category_best": 0,
            "lifetime_avg_wpm": float(wpm),
            "total_tests": 1,
            "wpm_diff_from_avg": 0.0,
            "is_demo": True,
            "session_weak_keys": sorted((errors_by_char or {}).items(), key=lambda x: x[1], reverse=True)[:5],
            "all_time_weak_keys": [],
        }

    user_data = load_history()
    summary = user_data.setdefault("summary", {})
    records = user_data.setdefault("records", {})
    sessions = user_data.setdefault("sessions", [])
    weak_keys = user_data.setdefault("weak_keys", {})

    category_key = f"{diff_key}_{length_key}"
    prev_record = records.get(category_key)
    prev_category_best = prev_record.get("wpm", 0) if prev_record else 0

    is_category_pb = wpm > prev_category_best
    is_overall_pb = wpm > summary.get("best_wpm", 0)

    words_typed = round(total_chars / 5)

    # Update summary
    summary["total_tests"] = summary.get("total_tests", 0) + 1
    summary["total_time_seconds"] = round(summary.get("total_time_seconds", 0.0) + elapsed, 2)
    summary["total_words"] = summary.get("total_words", 0) + words_typed
    if wpm > summary.get("best_wpm", 0):
        summary["best_wpm"] = wpm
    if accuracy > summary.get("best_accuracy", 0.0):
        summary["best_accuracy"] = round(accuracy, 1)

    # Update category personal best
    if is_category_pb or (prev_record and wpm == prev_category_best and accuracy > prev_record.get("accuracy", 0.0)):
        records[category_key] = {
            "diff_name": diff_name,
            "length_name": length_name,
            "wpm": wpm,
            "accuracy": round(accuracy, 1),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # Update Weak Keys database
    if errors_by_char:
        for ch, count in errors_by_char.items():
            if count > 0:
                weak_keys[ch] = weak_keys.get(ch, 0) + count

    # Record session entry
    session_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "diff_key": diff_key,
        "diff_name": diff_name,
        "length_key": length_key,
        "length_name": length_name,
        "wpm": wpm,
        "accuracy": round(accuracy, 1),
        "elapsed_seconds": round(elapsed, 2),
        "total_chars": total_chars,
        "errors": errors,
        "is_pb": is_category_pb,
    }
    sessions.append(session_entry)

    # Keep at most last 500 sessions
    if len(sessions) > 500:
        user_data["sessions"] = sessions[-500:]

    save_user_history(user_data)

    all_wpms = [s["wpm"] for s in sessions if "wpm" in s]
    lifetime_avg = round(sum(all_wpms) / len(all_wpms), 1) if all_wpms else float(wpm)

    session_top_stumbles = sorted((errors_by_char or {}).items(), key=lambda x: x[1], reverse=True)[:5]
    all_time_top_weak = get_top_weak_keys(top_n=5)

    return {
        "is_category_pb": is_category_pb,
        "is_overall_pb": is_overall_pb,
        "prev_category_best": prev_category_best,
        "lifetime_avg_wpm": lifetime_avg,
        "total_tests": summary["total_tests"],
        "wpm_diff_from_avg": round(wpm - lifetime_avg, 1),
        "is_demo": False,
        "session_weak_keys": session_top_stumbles,
        "all_time_weak_keys": all_time_top_weak,
    }


def compute_metrics(sessions: list) -> dict:
    """Computes rolling averages and summary stats from a list of sessions."""
    if not sessions:
        return {
            "total_tests": 0,
            "best_wpm": 0,
            "avg_wpm": 0.0,
            "best_acc": 0.0,
            "avg_acc": 0.0,
            "ao5": None,
            "ao10": None,
        }

    wpms = [s["wpm"] for s in sessions if "wpm" in s]
    accuracies = [s["accuracy"] for s in sessions if "accuracy" in s]

    total = len(wpms)
    best_wpm = max(wpms) if wpms else 0
    avg_wpm = round(sum(wpms) / total, 1) if total else 0.0
    best_acc = max(accuracies) if accuracies else 0.0
    avg_acc = round(sum(accuracies) / total, 1) if total else 0.0

    ao5 = None
    if len(wpms) >= 5:
        recent_5 = wpms[-5:]
        ao5 = round(sum(recent_5) / 5, 1)

    ao10 = None
    if len(wpms) >= 10:
        recent_10 = wpms[-10:]
        ao10 = round(sum(recent_10) / 10, 1)

    return {
        "total_tests": total,
        "best_wpm": best_wpm,
        "avg_wpm": avg_wpm,
        "best_acc": best_acc,
        "avg_acc": avg_acc,
        "ao5": ao5,
        "ao10": ao10,
    }


def generate_ascii_chart(sessions: list, max_points: int = 12, height: int = 5) -> list[str]:
    """Generates a clean ASCII line/plot chart representing WPM progression."""
    if not sessions or len(sessions) < 2:
        return ["  [ Complete at least 2 tests to display your speed trend chart ]"]

    recent = sessions[-max_points:]
    wpms = [s.get("wpm", 0) for s in recent]

    min_w = min(wpms)
    max_w = max(wpms)

    if min_w == max_w:
        max_w += 5
        min_w = max(0, min_w - 5)

    step = (max_w - min_w) / max(1, height)

    chart_lines = []
    for row in range(height, -1, -1):
        threshold = min_w + row * step
        label = f"{int(threshold):>3} WPM |"
        row_chars = []
        for i, val in enumerate(wpms):
            val_row = round((val - min_w) / max(1, (max_w - min_w)) * height)
            if val_row == row:
                row_chars.append(" * ")
            elif val_row > row:
                row_chars.append(" | ")
            else:
                row_chars.append("   ")
        chart_lines.append(label + "".join(row_chars))

    x_axis = "        +" + ("---" * len(wpms))
    chart_lines.append(x_axis)
    num_line = "         " + "".join(f"#{i+1:<2}" for i in range(len(wpms)))
    chart_lines.append(num_line)
    return chart_lines


def clear_history(username: str | None = None) -> bool:
    """Resets all typing history data for the specified or active user."""
    target = username or get_active_user()
    if target is None:
        return True

    fresh = _get_default_user_data(target)
    # Preserve salt and password
    current = load_history(target)
    fresh["salt"] = current.get("salt", "")
    fresh["password_hash"] = current.get("password_hash", "")
    return save_user_history(fresh, target)


def print_cli_stats(target_user: str | None = None):
    """Prints a clean ASCII stats dashboard directly to standard output (for CLI --stats)."""
    user_name = target_user or get_active_user() or get_last_active_user()
    data = load_history(user_name)

    summary = data.get("summary", {})
    sessions = data.get("sessions", [])
    records = data.get("records", {})
    metrics = compute_metrics(sessions)
    weak_keys = get_top_weak_keys(user_name, top_n=5)

    total_seconds = summary.get("total_time_seconds", 0.0)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    user_label = f"PROFILE: {user_name.upper()}" if user_name else "PROFILE: GUEST / DEMO"

    print("\n=======================================================")
    print(f"       TERMINAL TYPING SPEED STATS  ({user_label})")
    print("=======================================================\n")

    print(f"  Tests Completed:   {metrics['total_tests']}")
    print(f"  Total Words:       {summary.get('total_words', 0)}")
    print(f"  Total Practice:    {minutes}m {seconds}s")
    print(f"  Best Speed:        {metrics['best_wpm']} WPM")
    print(f"  Average Speed:     {metrics['avg_wpm']} WPM")
    print(f"  Best Accuracy:     {metrics['best_acc']:.1f}%")
    print(f"  Average Accuracy:  {metrics['avg_acc']:.1f}%")
    if metrics["ao5"] is not None:
        print(f"  Average of 5 (Ao5):  {metrics['ao5']} WPM")
    if metrics["ao10"] is not None:
        print(f"  Average of 10 (Ao10): {metrics['ao10']} WPM")

    # Top 5 Weak Keys Section
    print("\n---------------- TOP 5 WEAKEST KEYS ------------------\n")
    if weak_keys:
        total_errors_tracked = sum(data.get("weak_keys", {}).values())
        print(f"  {'Rank':<6} {'Key':<12} {'Errors':<10} {'% of Mistakes':<16}")
        print("  " + "-" * 44)
        for rank, (char, err_cnt) in enumerate(weak_keys, 1):
            pct = (err_cnt / total_errors_tracked) * 100 if total_errors_tracked else 0.0
            print(f"  #{rank:<5} {format_key_name(char):<12} {err_cnt:<10} {pct:5.1f}%")
        print("\n  [*] Practice Tip: Slow down slightly on these keys to boost accuracy!")
    else:
        print("  [ No errors recorded yet! Complete tests to identify weak keys ]")

    print("\n----------------- SPEED TREND CHART ------------------\n")
    chart_lines = generate_ascii_chart(sessions, max_points=12, height=6)
    for line in chart_lines:
        print(" " + line)

    if records:
        print("\n----------------- PERSONAL BESTS ---------------------\n")
        print(f"  {'Difficulty':<10} {'Length':<12} {'Best WPM':<10} {'Accuracy':<10} {'Date':<16}")
        print("  " + "-" * 58)
        for _, rec in sorted(records.items()):
            print(
                f"  {rec.get('diff_name', ''):<10} "
                f"{rec.get('length_name', ''):<12} "
                f"{rec.get('wpm', 0):<10} "
                f"{rec.get('accuracy', 0.0):.1f}%     "
                f"{rec.get('date', ''):<16}"
            )

    if sessions:
        print("\n---------------- RECENT SESSIONS (LAST 5) ------------\n")
        print(f"  {'Date & Time':<17} {'Mode':<18} {'WPM':<8} {'Acc %':<8} {'Time':<8} {'PB'}")
        print("  " + "-" * 66)
        for s in sessions[-5:]:
            mode = f"{s.get('diff_name', '')} ({s.get('length_name', '')})"
            pb_tag = "[PB]" if s.get("is_pb") else ""
            print(
                f"  {s.get('timestamp', ''):<17} "
                f"{mode:<18} "
                f"{s.get('wpm', 0):<8} "
                f"{s.get('accuracy', 0.0):.1f}%    "
                f"{s.get('elapsed_seconds', 0.0):.1f}s    "
                f"{pb_tag}"
            )

    print("\n=======================================================\n")
