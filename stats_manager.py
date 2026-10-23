"""
Stats Manager for Terminal Speed Typing Test.
Handles persistent storage of test metrics, personal bests, rolling averages,
ASCII trend charts, and command-line summaries.
"""

import json
import os
import sys
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
        # Test writeability
        if not home_path.exists():
            home_path.touch(exist_ok=True)
        return home_path
    except Exception:
        return Path(__file__).resolve().parent / "typing_history.json"


HISTORY_FILE = get_history_file_path()


def _get_default_data() -> dict:
    return {
        "version": 1,
        "summary": {
            "total_tests": 0,
            "total_time_seconds": 0.0,
            "total_words": 0,
            "best_wpm": 0,
            "best_accuracy": 0.0,
        },
        "records": {},  # key: f"{diff}_{length}", value: {"wpm": ..., "accuracy": ..., "date": ...}
        "sessions": [],  # list of session dicts (most recent last)
    }


def load_history() -> dict:
    """Loads history from JSON file, returning a clean dictionary structure."""
    if not HISTORY_FILE.exists():
        return _get_default_data()

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return _get_default_data()
            if "summary" not in data or "sessions" not in data:
                return _get_default_data()
            return data
    except Exception:
        return _get_default_data()


def save_history(data: dict) -> bool:
    """Saves history data to the JSON file safely."""
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Warning: Failed to save typing history: {e}", file=sys.stderr)
        return False


def record_session(
    diff_key: str,
    diff_name: str,
    length_key: str,
    length_name: str,
    wpm: int,
    accuracy: float,
    elapsed: float,
    total_chars: int,
    errors: int
) -> dict:
    """
    Records a completed typing session, updates personal bests, and returns
    a performance assessment with personal best status and comparisons.
    """
    data = load_history()
    summary = data["summary"]
    records = data.setdefault("records", {})
    sessions = data.setdefault("sessions", [])

    category_key = f"{diff_key}_{length_key}"
    prev_record = records.get(category_key)
    prev_category_best = prev_record.get("wpm", 0) if prev_record else 0

    is_category_pb = wpm > prev_category_best
    is_overall_pb = wpm > summary.get("best_wpm", 0)

    # Calculate estimated words (5 chars per word standard)
    words_typed = round(total_chars / 5)

    # Update summary
    summary["total_tests"] = summary.get("total_tests", 0) + 1
    summary["total_time_seconds"] = round(summary.get("total_time_seconds", 0.0) + elapsed, 2)
    summary["total_words"] = summary.get("total_words", 0) + words_typed
    if wpm > summary.get("best_wpm", 0):
        summary["best_wpm"] = wpm
    if accuracy > summary.get("best_accuracy", 0.0):
        summary["best_accuracy"] = round(accuracy, 1)

    # Update category record if higher WPM or equal WPM with better accuracy
    if is_category_pb or (prev_record and wpm == prev_category_best and accuracy > prev_record.get("accuracy", 0.0)):
        records[category_key] = {
            "diff_name": diff_name,
            "length_name": length_name,
            "wpm": wpm,
            "accuracy": round(accuracy, 1),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # Record session
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

    # Keep at most last 500 sessions to keep file size lightweight
    if len(sessions) > 500:
        data["sessions"] = sessions[-500:]

    save_history(data)

    # Calculate average of all sessions
    all_wpms = [s["wpm"] for s in sessions if "wpm" in s]
    lifetime_avg = round(sum(all_wpms) / len(all_wpms), 1) if all_wpms else float(wpm)

    return {
        "is_category_pb": is_category_pb,
        "is_overall_pb": is_overall_pb,
        "prev_category_best": prev_category_best,
        "lifetime_avg_wpm": lifetime_avg,
        "total_tests": summary["total_tests"],
        "wpm_diff_from_avg": round(wpm - lifetime_avg, 1),
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

    # Rolling averages (Ao5 and Ao10)
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
    """
    Generates a clean ASCII line/plot chart representing WPM progression.
    Returns a list of formatted strings ready to be rendered in curses or CMD.
    """
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
    # Build chart rows from top to bottom
    for row in range(height, -1, -1):
        threshold = min_w + row * step
        label = f"{int(threshold):>3} WPM |"
        row_chars = []
        for i, val in enumerate(wpms):
            # Check if this point falls near this row's threshold
            val_row = round((val - min_w) / max(1, (max_w - min_w)) * height)
            if val_row == row:
                row_chars.append(" * ")
            elif val_row > row:
                row_chars.append(" | ")
            else:
                row_chars.append("   ")
        chart_lines.append(label + "".join(row_chars))

    # X-axis bottom line
    x_axis = "        +" + ("---" * len(wpms))
    chart_lines.append(x_axis)

    # X-axis test numbering
    num_line = "         " + "".join(f"#{i+1:<2}" for i in range(len(wpms)))
    chart_lines.append(num_line)

    return chart_lines


def generate_sparkline(sessions: list, max_points: int = 15) -> str:
    """Generates a compact sparkline string from recent sessions."""
    if not sessions:
        return ""
    recent = sessions[-max_points:]
    wpms = [s.get("wpm", 0) for s in recent]
    bars = ["_", ".", "-", "=", "#"]
    min_w, max_w = min(wpms), max(wpms)
    span = max(1, max_w - min_w)

    chars = []
    for w in wpms:
        idx = min(len(bars) - 1, int(((w - min_w) / span) * len(bars)))
        chars.append(bars[idx])
    return "".join(chars)


def clear_history() -> bool:
    """Resets all typing history data."""
    return save_history(_get_default_data())


def print_cli_stats():
    """Prints a clean ASCII stats dashboard directly to standard output (for CLI --stats)."""
    data = load_history()
    summary = data.get("summary", {})
    sessions = data.get("sessions", [])
    records = data.get("records", {})
    metrics = compute_metrics(sessions)

    total_seconds = summary.get("total_time_seconds", 0.0)
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    print("\n=======================================================")
    print("             TERMINAL TYPING SPEED STATS               ")
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
