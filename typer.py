import curses
from curses import wrapper
import time
import random
import sys
import stats_manager
from texts import DATASET


def safe_addstr(stdscr, y, x, text, attr=0):
    """Safely adds string to curses window without crashing on terminal edge."""
    h, w = stdscr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        available = w - x
        if y == h - 1:
            available -= 1
        if available > 0:
            try:
                stdscr.addstr(y, x, text[:available], attr)
            except curses.error:
                pass


def layout_text(text, max_width):
    """
    Computes (row, col) coordinates for each character in text,
    wrapping words cleanly at max_width without truncating words.
    """
    words = text.split(" ")
    char_positions = []
    curr_row = 0
    curr_col = 0

    for w_idx, word in enumerate(words):
        word_with_space = word if w_idx == len(words) - 1 else word + " "
        if curr_col + len(word) > max_width and curr_col > 0:
            curr_row += 1
            curr_col = 0

        for ch in word_with_space:
            char_positions.append((curr_row, curr_col, ch))
            curr_col += 1

    total_rows = curr_row + 1
    return char_positions, total_rows


def prompt_text_input(stdscr, y, x, prompt_label, is_password=False, max_len=20) -> str | None:
    """
    Interactive single-line text input field in curses.
    Supports typing, backspace, Enter (confirm), and ESC (cancel).
    Masks with '*' if is_password is True.
    """
    curses.curs_set(1)
    stdscr.nodelay(False)
    buffer = []

    while True:
        display_str = ("*" * len(buffer)) if is_password else "".join(buffer)
        prompt_line = f"{prompt_label}: {display_str} "
        safe_addstr(stdscr, y, x, prompt_line + "   ", curses.color_pair(3) | curses.A_BOLD)
        stdscr.move(y, x + len(prompt_label) + 2 + len(buffer))
        stdscr.refresh()

        ch = stdscr.getch()
        if ch == 27:  # ESC cancels
            curses.curs_set(0)
            return None
        elif ch in (10, 13, curses.KEY_ENTER):
            curses.curs_set(0)
            return "".join(buffer).strip()
        elif ch in (curses.KEY_BACKSPACE, 8, 127):
            if buffer:
                buffer.pop()
        elif 32 <= ch <= 126 and len(buffer) < max_len:
            buffer.append(chr(ch))


def auth_screen(stdscr) -> bool:
    """
    Screen 0: Welcome & User Profile Selection.
    Options:
      [1] Login (Existing User)
      [2] Create New Profile
      [3] Demo Mode (No stats saved)
      [ESC] Quit
    Returns True if user logged in or entered Demo mode, False to quit.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)

    message = ""
    message_color = curses.color_pair(5)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "=== SPEED TYPER - USER PROFILES ==="
        subtitle = "Multi-User Typing Speed Test with Weak Key Diagnostics"

        safe_addstr(stdscr, max(1, h // 2 - 8), max(0, (w - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(stdscr, max(2, h // 2 - 6), max(0, (w - len(subtitle)) // 2), subtitle, curses.color_pair(4))

        registered_users = stats_manager.list_users()
        user_count_str = f"Registered Profiles: {len(registered_users)}"
        safe_addstr(stdscr, max(3, h // 2 - 4), max(0, (w - len(user_count_str)) // 2), user_count_str, curses.color_pair(5))

        options = [
            ("[1] Login", "Select an existing user profile and enter password"),
            ("[2] Create Profile", "Create a new profile with username & password"),
            ("[3] Demo Mode", "Practice without recording statistics or weak keys"),
            ("[ESC] Quit", "Exit the application"),
        ]

        start_y = max(5, h // 2 - 2)
        for idx, (label, desc) in enumerate(options):
            line = f"  {label:<18} - {desc}"
            attr = curses.color_pair(5) | curses.A_BOLD if idx == 0 else curses.color_pair(4)
            safe_addstr(stdscr, start_y + (idx * 2), max(2, (w - 70) // 2), line, attr)

        if message:
            safe_addstr(stdscr, start_y + len(options) * 2 + 1, max(0, (w - len(message)) // 2), message, message_color | curses.A_BOLD)

        footer = "Press [1], [2], [3], or [ESC]"
        safe_addstr(stdscr, h - 2, max(0, (w - len(footer)) // 2), footer, curses.color_pair(3))

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == 27:  # ESC
            return False

        elif ch in (ord("1"),):
            # Login
            if not registered_users:
                message = "No profiles found yet! Press [2] to create your first profile."
                message_color = curses.color_pair(5)
                continue

            # Prompt username
            stdscr.erase()
            login_title = "=== USER LOGIN ==="
            safe_addstr(stdscr, max(1, h // 2 - 6), max(0, (w - len(login_title)) // 2), login_title, curses.color_pair(3) | curses.A_BOLD)

            users_preview = "Available profiles: " + ", ".join(registered_users[:8])
            safe_addstr(stdscr, max(2, h // 2 - 4), max(0, (w - len(users_preview)) // 2), users_preview, curses.color_pair(4))

            input_y = max(4, h // 2 - 1)
            input_x = max(2, (w - 36) // 2)

            username = prompt_text_input(stdscr, input_y, input_x, "Username", is_password=False)
            if not username:
                message = "Login cancelled."
                message_color = curses.color_pair(4)
                continue

            password = prompt_text_input(stdscr, input_y + 2, input_x, "Password", is_password=True)
            if password is None:
                message = "Login cancelled."
                message_color = curses.color_pair(4)
                continue

            ok, res_msg = stats_manager.authenticate(username, password)
            if ok:
                return True
            else:
                message = f"Error: {res_msg}"
                message_color = curses.color_pair(2)

        elif ch in (ord("2"),):
            # Create Profile
            stdscr.erase()
            create_title = "=== CREATE NEW PROFILE ==="
            safe_addstr(stdscr, max(1, h // 2 - 6), max(0, (w - len(create_title)) // 2), create_title, curses.color_pair(3) | curses.A_BOLD)

            hint = "Choose a simple username and password (saved locally on your machine)"
            safe_addstr(stdscr, max(2, h // 2 - 4), max(0, (w - len(hint)) // 2), hint, curses.color_pair(4))

            input_y = max(4, h // 2 - 1)
            input_x = max(2, (w - 40) // 2)

            username = prompt_text_input(stdscr, input_y, input_x, "New Username", is_password=False)
            if not username:
                message = "Profile creation cancelled."
                message_color = curses.color_pair(4)
                continue

            password = prompt_text_input(stdscr, input_y + 2, input_x, "Password", is_password=True)
            if password is None:
                message = "Profile creation cancelled."
                message_color = curses.color_pair(4)
                continue

            confirm_pass = prompt_text_input(stdscr, input_y + 4, input_x, "Confirm Password", is_password=True)
            if confirm_pass != password:
                message = "Error: Passwords do not match. Please try again."
                message_color = curses.color_pair(2)
                continue

            ok, res_msg = stats_manager.create_user(username, password)
            if ok:
                return True
            else:
                message = f"Error: {res_msg}"
                message_color = curses.color_pair(2)

        elif ch in (ord("3"),):
            # Demo Mode
            stats_manager.set_demo_mode()
            return True


def get_user_header_tag() -> str:
    """Returns a visual badge showing the current user or Demo mode."""
    if stats_manager.is_demo_mode():
        return "[DEMO MODE - STATS NOT SAVED]"
    user = stats_manager.get_active_user()
    return f"[USER: {user.upper()}]" if user else "[GUEST]"


def difficulty_menu(stdscr):
    """
    Step 1: Select Difficulty Level (Easy, Medium, Hard), View Stats, or Switch User.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    diff_keys = ["easy", "medium", "hard"]
    options = [
        ("1", "Easy", "Normal words only, simple and clean"),
        ("2", "Medium", "Everyday punctuation, quotes, numbers, and contractions"),
        ("3", "Hard", "Special characters, brackets, symbols, and technical syntax"),
        ("S", "Stats Dashboard", "View lifetime stats, ASCII speed trend, and weak keys"),
        ("U", "Switch Profile", "Change user profile or switch to/from Demo mode"),
    ]
    selected_idx = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "=== TERMINAL SPEED TYPING TEST ==="
        user_tag = get_user_header_tag()
        user_color = curses.color_pair(6) if stats_manager.is_demo_mode() else curses.color_pair(5)

        safe_addstr(stdscr, max(0, h // 2 - 8), max(0, (w - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(stdscr, max(1, h // 2 - 7), max(0, (w - len(user_tag)) // 2), user_tag, user_color | curses.A_BOLD)

        subtitle = "STEP 1: Select Difficulty"
        safe_addstr(stdscr, max(2, h // 2 - 5), max(0, (w - len(subtitle)) // 2), subtitle, curses.color_pair(4))

        for idx, (key, name, desc) in enumerate(options):
            item_text = f" [{key}] {name} - {desc} "
            y = h // 2 - 3 + (idx * 2)
            x = max(2, (w - len(item_text)) // 2)

            if idx == selected_idx:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(4))

        instructions = "Use [UP / DOWN] & [ENTER], press [1-3], [S] for Stats, [U] for User, or [ESC] to exit"
        safe_addstr(stdscr, max(0, h // 2 + 8), max(0, (w - len(instructions)) // 2), instructions, curses.color_pair(3))

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == 27:  # ESC exits
            return None
        elif ch in (curses.KEY_UP, ord("k"), ord("K")):
            selected_idx = (selected_idx - 1) % len(options)
        elif ch in (curses.KEY_DOWN, ord("j"), ord("J")):
            selected_idx = (selected_idx + 1) % len(options)
        elif ch in (10, 13, curses.KEY_ENTER):
            chosen_key = options[selected_idx][0]
            if chosen_key == "1":
                return "easy"
            elif chosen_key == "2":
                return "medium"
            elif chosen_key == "3":
                return "hard"
            elif chosen_key == "S":
                return "stats"
            elif chosen_key == "U":
                return "switch_user"
        elif ch in (ord("1"), ord("e"), ord("E")):
            return "easy"
        elif ch in (ord("2"), ord("m"), ord("M")):
            return "medium"
        elif ch in (ord("3"), ord("h"), ord("H")):
            return "hard"
        elif ch in (ord("s"), ord("S")):
            return "stats"
        elif ch in (ord("u"), ord("U")):
            return "switch_user"


def length_menu(stdscr, diff_key):
    """
    Step 2: Select Text Length (One Line, Stanza, One Page).
    """
    curses.curs_set(0)
    stdscr.nodelay(False)
    diff_name = DATASET[diff_key]["name"]
    lengths = DATASET[diff_key]["lengths"]
    length_keys = ["1", "2", "3"]
    selected_idx = 0

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = f"=== SPEED TYPING TEST [{diff_name.upper()}] ==="
        user_tag = get_user_header_tag()
        user_color = curses.color_pair(6) if stats_manager.is_demo_mode() else curses.color_pair(5)

        safe_addstr(stdscr, max(0, h // 2 - 8), max(0, (w - len(title)) // 2), title, curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(stdscr, max(1, h // 2 - 7), max(0, (w - len(user_tag)) // 2), user_tag, user_color | curses.A_BOLD)

        subtitle = "STEP 2: Select Text Length"
        safe_addstr(stdscr, max(2, h // 2 - 5), max(0, (w - len(subtitle)) // 2), subtitle, curses.color_pair(4))

        for idx, key in enumerate(length_keys):
            info = lengths[key]
            item_text = f" [{key}] {info['name']} - {info['description']} "
            y = h // 2 - 2 + (idx * 2)
            x = max(2, (w - len(item_text)) // 2)

            if idx == selected_idx:
                stdscr.attron(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            else:
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(y, x, item_text)
                stdscr.attroff(curses.color_pair(4))

        instructions = "Use [UP / DOWN] & [ENTER], press [1-3], or [ESC] to go back"
        safe_addstr(stdscr, max(0, h // 2 + 6), max(0, (w - len(instructions)) // 2), instructions, curses.color_pair(3))

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == 27:  # ESC goes back
            return None
        elif ch in (curses.KEY_UP, ord("k"), ord("K")):
            selected_idx = (selected_idx - 1) % len(length_keys)
        elif ch in (curses.KEY_DOWN, ord("j"), ord("J")):
            selected_idx = (selected_idx + 1) % len(length_keys)
        elif ch in (10, 13, curses.KEY_ENTER):
            return length_keys[selected_idx]
        elif ch in (ord("1"), ord("2"), ord("3")):
            return chr(ch)


def display_typing_arena(
    stdscr, diff_name, length_name, target_text, current_text, char_positions, total_rows, wpm, accuracy, elapsed
):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # User Tag / Demo Tag
    user_tag = get_user_header_tag()
    user_color = curses.color_pair(6) if stats_manager.is_demo_mode() else curses.color_pair(5)

    header = f" SPEED TYPING TEST  [{diff_name.upper()} | {length_name.upper()}]  {user_tag} "
    safe_addstr(stdscr, 1, max(0, (w - len(header)) // 2), header, curses.color_pair(3) | curses.A_BOLD)

    # Progress %
    progress = (len(current_text) / len(target_text)) * 100 if target_text else 0.0

    # Live HUD Bar
    stats = f"  WPM: {wpm:3d}  |  Accuracy: {accuracy:5.1f}%  |  Time: {elapsed:4.1f}s  |  Progress: {progress:3.0f}%  |  [ESC: Menu]  "
    safe_addstr(stdscr, 3, max(0, (w - len(stats)) // 2), stats, curses.color_pair(5))

    # Divider
    divider_len = min(w - 4, 84)
    divider = "-" * divider_len
    safe_addstr(stdscr, 4, max(0, (w - divider_len) // 2), divider, curses.color_pair(4))

    # Text rendering area
    start_y = 6
    max_visible_rows = max(4, h - start_y - 3)
    max_width = min(80, max(20, w - 8))
    start_x = max(2, (w - max_width) // 2)

    # Current typing position row
    if len(current_text) < len(char_positions):
        current_cursor_row = char_positions[len(current_text)][0]
    else:
        current_cursor_row = char_positions[-1][0] if char_positions else 0

    # Auto-scroll offset
    if total_rows > max_visible_rows:
        scroll_row = max(0, current_cursor_row - (max_visible_rows // 2))
        scroll_row = min(scroll_row, max(0, total_rows - max_visible_rows))
    else:
        scroll_row = 0

    # Render characters
    typed_len = len(current_text)
    for idx, (r, c, target_ch) in enumerate(char_positions):
        screen_r = start_y + (r - scroll_row)
        if start_y <= screen_r < start_y + max_visible_rows:
            screen_c = start_x + c
            if screen_c < w - 1:
                if idx < typed_len:
                    user_ch = current_text[idx]
                    if user_ch == target_ch:
                        color = curses.color_pair(1)  # Green
                    else:
                        color = curses.color_pair(2)  # Red
                    stdscr.attron(color)
                    stdscr.addstr(screen_r, screen_c, user_ch)
                    stdscr.attroff(color)
                elif idx == typed_len:
                    stdscr.attron(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(3) | curses.A_UNDERLINE | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(screen_r, screen_c, target_ch)
                    stdscr.attroff(curses.color_pair(4))

    if total_rows > max_visible_rows:
        indicator = f" [Lines {scroll_row + 1}-{min(total_rows, scroll_row + max_visible_rows)} of {total_rows}] "
        safe_addstr(stdscr, h - 2, max(0, (w - len(indicator)) // 2), indicator, curses.color_pair(4))

    stdscr.refresh()


def result_screen(
    stdscr, diff_key, diff_name, length_key, length_name, wpm, accuracy, elapsed, total_chars, errors, errors_by_char
):
    stdscr.nodelay(False)
    curses.curs_set(0)
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    # Record session & get stats comparison
    stats_info = stats_manager.record_session(
        diff_key,
        diff_name,
        length_key,
        length_name,
        wpm,
        accuracy,
        elapsed,
        total_chars,
        errors,
        errors_by_char=errors_by_char,
    )

    y_offset = max(1, h // 2 - 9)

    # Demo mode notification or Personal Best alert
    if stats_info.get("is_demo"):
        demo_banner = "[ DEMO MODE: Test completed, but results are NOT saved to stats ]"
        safe_addstr(stdscr, y_offset, max(0, (w - len(demo_banner)) // 2), demo_banner, curses.color_pair(6) | curses.A_BOLD)
        y_offset += 2
    elif stats_info.get("is_category_pb"):
        prev_best = stats_info.get("prev_category_best", 0)
        pb_banner = f"*** NEW PERSONAL BEST! (Previous: {prev_best} WPM -> Now: {wpm} WPM) ***"
        safe_addstr(stdscr, y_offset, max(0, (w - len(pb_banner)) // 2), pb_banner, curses.color_pair(5) | curses.A_BOLD)
        y_offset += 2

    banner = "=== TEST COMPLETE! ==="
    safe_addstr(stdscr, y_offset, max(0, (w - len(banner)) // 2), banner, curses.color_pair(1) | curses.A_BOLD)
    y_offset += 2

    user_tag = get_user_header_tag()
    config_info = f"Profile: {user_tag}   |   Difficulty: {diff_name}   |   Length: {length_name}"
    safe_addstr(stdscr, y_offset, max(0, (w - len(config_info)) // 2), config_info, curses.color_pair(3))
    y_offset += 2

    lifetime_avg = stats_info.get("lifetime_avg_wpm", float(wpm))
    diff_from_avg = stats_info.get("wpm_diff_from_avg", 0.0)
    avg_comparison = (
        f"({diff_from_avg:+.1f} vs lifetime avg of {lifetime_avg:.1f} WPM)" if not stats_info.get("is_demo") else ""
    )

    lines = [
        f"Typing Speed:    {wpm} Words Per Minute (WPM) {avg_comparison}",
        f"Accuracy:        {accuracy:.1f}%",
        f"Time Elapsed:    {elapsed:.2f} seconds",
        f"Characters:      {total_chars} typed ({errors} errors)",
    ]

    for idx, line in enumerate(lines):
        y = y_offset + idx
        x = max(0, (w - len(line)) // 2)
        attr = curses.color_pair(5) | curses.A_BOLD if idx == 0 else curses.color_pair(4)
        safe_addstr(stdscr, y, x, line, attr)

    y_offset += len(lines) + 1

    # WEAK KEYS SECTION: Display keys that stumbled in this session
    session_stumbles = stats_info.get("session_weak_keys", [])
    if session_stumbles:
        stumble_items = [f"{stats_manager.format_key_name(k)}: {cnt}x" for k, cnt in session_stumbles]
        stumble_line = "Keys Missed in this Test:  " + "   ".join(stumble_items)
        safe_addstr(stdscr, y_offset, max(0, (w - len(stumble_line)) // 2), stumble_line, curses.color_pair(2) | curses.A_BOLD)
        y_offset += 1

    # All-time top weak keys
    all_time_weak = stats_info.get("all_time_weak_keys", [])
    if all_time_weak and not stats_info.get("is_demo"):
        weak_items = [f"#{i+1} {stats_manager.format_key_name(k)} ({cnt} errs)" for i, (k, cnt) in enumerate(all_time_weak[:4])]
        weak_line = "Top Stumbling Keys (All-Time):  " + "  |  ".join(weak_items)
        safe_addstr(stdscr, y_offset, max(0, (w - len(weak_line)) // 2), weak_line, curses.color_pair(5))
        y_offset += 1
        tip = "[*] Tip: Slow down slightly on your weak keys to boost overall accuracy!"
        safe_addstr(stdscr, y_offset, max(0, (w - len(tip)) // 2), tip, curses.color_pair(3))
        y_offset += 1

    prompt = "Press [ENTER] to play again, [M] for Menu, [S] for Stats, or [ESC] to quit"
    safe_addstr(stdscr, y_offset + 2, max(0, (w - len(prompt)) // 2), prompt, curses.A_BLINK | curses.color_pair(3))

    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        if ch == 27:  # ESC
            return "quit"
        elif ch in (ord("m"), ord("M")):
            return "menu"
        elif ch in (ord("s"), ord("S")):
            stats_dashboard(stdscr)
            return "menu"
        elif ch in (10, 13, curses.KEY_ENTER, ord(" ")):
            return "again"


def stats_dashboard(stdscr):
    """
    Dedicated curses screen for viewing lifetime stats, rolling averages,
    ASCII speed trend chart, Top 5 Weak Keys, and recent sessions.
    Designed with a clean, structured, easy-to-read frame layout.
    """
    curses.curs_set(0)
    stdscr.nodelay(False)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        active_user = stats_manager.get_active_user()
        data = stats_manager.load_history()
        summary = data.get("summary", {})
        sessions = data.get("sessions", [])
        metrics = stats_manager.compute_metrics(sessions)
        weak_keys = stats_manager.get_top_weak_keys(top_n=5)

        box_w = min(74, max(52, w - 4))
        start_x = max(1, (w - box_w) // 2)

        # Header Box
        user_name = active_user.upper() if active_user else "GUEST / DEMO"
        title_text = f" TYPING PROGRESS DASHBOARD  •  PROFILE: {user_name} "
        border_line = "=" * box_w
        div_line = "-" * (box_w - 4)

        safe_addstr(stdscr, 1, start_x, border_line, curses.color_pair(3))
        safe_addstr(stdscr, 2, start_x + max(0, (box_w - len(title_text)) // 2), title_text, curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(stdscr, 3, start_x, border_line, curses.color_pair(3))

        if stats_manager.is_demo_mode():
            demo_msg = "  [DEMO MODE ACTIVE] Tests taken in Demo mode are not saved."
            safe_addstr(stdscr, 5, start_x, demo_msg, curses.color_pair(6) | curses.A_BOLD)
            hint_msg = "  Create or log into a profile to save personal bests and track weak keys."
            safe_addstr(stdscr, 7, start_x, hint_msg, curses.color_pair(4))
            prompt = "[U] Login / Create Profile       [ESC / ENTER] Back to Menu"
            safe_addstr(stdscr, h - 2, max(0, (w - len(prompt)) // 2), prompt, curses.color_pair(3) | curses.A_BOLD)
            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (ord("u"), ord("U")):
                if auth_screen(stdscr):
                    continue
                return
            elif ch in (27, 10, 13, curses.KEY_ENTER, ord("b"), ord("B"), ord("q"), ord("Q")):
                return
            continue

        # SECTION 1: PERFORMANCE OVERVIEW (Clean 2-column key/value grid)
        total_sec = summary.get("total_time_seconds", 0.0)
        mins = int(total_sec // 60)
        secs = int(total_sec % 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        ao5_str = f"{metrics['ao5']} WPM" if metrics["ao5"] is not None else "--"
        ao10_str = f"{metrics['ao10']} WPM" if metrics["ao10"] is not None else "--"

        safe_addstr(stdscr, 5, start_x + 2, "PERFORMANCE OVERVIEW", curses.color_pair(5) | curses.A_BOLD)
        safe_addstr(stdscr, 6, start_x + 2, div_line, curses.color_pair(4))

        col2_offset = (box_w - 4) // 2

        # Row 1
        safe_addstr(stdscr, 7, start_x + 2, f"Tests Taken:    {metrics['total_tests']:<6}", curses.color_pair(4))
        safe_addstr(stdscr, 7, start_x + 2 + col2_offset, f"Practice Time:    {time_str}", curses.color_pair(4))

        # Row 2
        safe_addstr(stdscr, 8, start_x + 2, f"Words Typed:    {summary.get('total_words', 0):<6}", curses.color_pair(4))
        safe_addstr(stdscr, 8, start_x + 2 + col2_offset, f"Best Accuracy:    {metrics['best_acc']:.1f}%", curses.color_pair(4))

        # Row 3
        safe_addstr(stdscr, 9, start_x + 2, f"Top Speed:      {metrics['best_wpm']} WPM", curses.color_pair(1) | curses.A_BOLD)
        safe_addstr(stdscr, 9, start_x + 2 + col2_offset, f"Average Speed:    {metrics['avg_wpm']:.1f} WPM", curses.color_pair(5) | curses.A_BOLD)

        # Row 4 (Rolling averages)
        safe_addstr(stdscr, 10, start_x + 2, f"Rolling (Ao5):  {ao5_str}", curses.color_pair(4))
        safe_addstr(stdscr, 10, start_x + 2 + col2_offset, f"Rolling (Ao10):   {ao10_str}", curses.color_pair(4))

        # SECTION 2: WEAKEST KEYS (CLEAN & READABLE)
        curr_y = 12
        safe_addstr(stdscr, curr_y, start_x + 2, "WEAKEST KEYS (NEEDS FOCUS)", curses.color_pair(2) | curses.A_BOLD)
        curr_y += 1
        safe_addstr(stdscr, curr_y, start_x + 2, div_line, curses.color_pair(4))
        curr_y += 1

        if weak_keys:
            total_mistakes = sum(data.get("weak_keys", {}).values())
            # Line 1: keys 1 to 3
            l1_parts = []
            for rank, (k, cnt) in enumerate(weak_keys[:3], 1):
                pct = (cnt / total_mistakes) * 100 if total_mistakes else 0
                l1_parts.append(f"{rank}. {stats_manager.format_key_name(k)}: {cnt} err ({pct:.0f}%)")
            safe_addstr(stdscr, curr_y, start_x + 2, "     ".join(l1_parts), curses.color_pair(5))
            curr_y += 1

            # Line 2: keys 4 to 5 (if any)
            if len(weak_keys) > 3:
                l2_parts = []
                for rank, (k, cnt) in enumerate(weak_keys[3:5], 4):
                    pct = (cnt / total_mistakes) * 100 if total_mistakes else 0
                    l2_parts.append(f"{rank}. {stats_manager.format_key_name(k)}: {cnt} err ({pct:.0f}%)")
                safe_addstr(stdscr, curr_y, start_x + 2, "     ".join(l2_parts), curses.color_pair(5))
                curr_y += 1
        else:
            safe_addstr(stdscr, curr_y, start_x + 2, "[ No errors recorded yet! Complete more tests to diagnose weak keys ]", curses.color_pair(4))
            curr_y += 1

        curr_y += 1

        # SECTION 3: RECENT SPEED TREND
        if h >= curr_y + 10:
            safe_addstr(stdscr, curr_y, start_x + 2, "SPEED PROGRESSION (LAST 10 TESTS)", curses.color_pair(3) | curses.A_BOLD)
            curr_y += 1
            safe_addstr(stdscr, curr_y, start_x + 2, div_line, curses.color_pair(4))
            curr_y += 1

            chart_lines = stats_manager.generate_ascii_chart(sessions, max_points=10, height=3)
            for c_line in chart_lines:
                safe_addstr(stdscr, curr_y, start_x + 2, c_line, curses.color_pair(4))
                curr_y += 1
            curr_y += 1

        # SECTION 4: RECENT TEST HISTORY
        if h >= curr_y + 6:
            safe_addstr(stdscr, curr_y, start_x + 2, "RECENT TEST HISTORY", curses.color_pair(5) | curses.A_BOLD)
            curr_y += 1
            safe_addstr(stdscr, curr_y, start_x + 2, div_line, curses.color_pair(4))
            curr_y += 1

            tbl_header = f"  {'TIME':<7} {'MODE':<20} {'WPM':<7} {'ACCURACY':<11} {'TIME':<9} {'STATUS'}"
            safe_addstr(stdscr, curr_y, start_x, tbl_header, curses.color_pair(3) | curses.A_BOLD)
            curr_y += 1

            max_rows = min(3, max(1, h - curr_y - 3))
            recent_reversed = list(reversed(sessions))[:max_rows]
            for s in recent_reversed:
                ts = s.get("timestamp", "")
                time_only = ts.split(" ")[-1] if " " in ts else ts
                diff = s.get("diff_name", "Easy")
                length = s.get("length_name", "One Line")
                mode_str = f"{diff} ({length})"[:19]
                wpm_val = s.get("wpm", 0)
                acc = s.get("accuracy", 0.0)
                dur = f"{s.get('elapsed_seconds', 0.0):.1f}s"
                pb_str = "[PB]" if s.get("is_pb") else ""

                row_str = f"  {time_only:<7} {mode_str:<20} {wpm_val:<7} {acc:5.1f}%      {dur:<9} {pb_str}"
                attr = curses.color_pair(1) | curses.A_BOLD if s.get("is_pb") else curses.color_pair(4)
                safe_addstr(stdscr, curr_y, start_x, row_str, attr)
                curr_y += 1

        # Footer controls
        prompt = "[C] Clear My Stats     [U] Switch Profile     [ESC / ENTER] Back to Menu"
        safe_addstr(stdscr, h - 2, max(0, (w - len(prompt)) // 2), prompt, curses.color_pair(3) | curses.A_BOLD)

        stdscr.refresh()
        ch = stdscr.getch()

        if ch in (27, 10, 13, curses.KEY_ENTER, ord("b"), ord("B"), ord("q"), ord("Q")):
            return
        elif ch in (ord("u"), ord("U")):
            if auth_screen(stdscr):
                continue
            return
        elif ch in (ord("c"), ord("C")):
            confirm_msg = f"Reset all stats for profile '{active_user}'? [Y / N]: "
            safe_addstr(stdscr, h - 2, max(0, (w - len(confirm_msg)) // 2), confirm_msg, curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            conf_ch = stdscr.getch()
            if conf_ch in (ord("y"), ord("Y")):
                stats_manager.clear_history()


def run_test(stdscr, diff_key, length_key):
    diff_name = DATASET[diff_key]["name"]
    length_info = DATASET[diff_key]["lengths"][length_key]
    length_name = length_info["name"]
    target_text = random.choice(length_info["texts"])
    current_text = []

    h, w = stdscr.getmaxyx()
    max_width = min(80, max(20, w - 8))
    char_positions, total_rows = layout_text(target_text, max_width)

    start_time = None
    errors = 0
    total_keystrokes = 0
    errors_by_char = {}  # Tracks which characters were stumbled upon!

    stdscr.nodelay(True)

    while True:
        elapsed_time = max(time.time() - start_time, 0.1) if start_time else 0.0

        if elapsed_time > 0 and start_time is not None:
            wpm = round((len(current_text) / 5) / (elapsed_time / 60))
        else:
            wpm = 0

        if total_keystrokes > 0:
            accuracy = max(0.0, ((total_keystrokes - errors) / total_keystrokes) * 100.0)
        else:
            accuracy = 100.0

        display_typing_arena(
            stdscr,
            diff_name,
            length_name,
            target_text,
            current_text,
            char_positions,
            total_rows,
            wpm,
            accuracy,
            elapsed_time,
        )

        if len(current_text) == len(target_text):
            action = result_screen(
                stdscr,
                diff_key,
                diff_name,
                length_key,
                length_name,
                wpm,
                accuracy,
                elapsed_time,
                len(current_text),
                errors,
                errors_by_char,
            )
            return action

        ch = stdscr.getch()

        if ch == -1:
            time.sleep(0.02)
            continue

        if ch == 27:  # ESC to return to menu
            return "menu"

        if ch == curses.KEY_RESIZE:
            h, w = stdscr.getmaxyx()
            max_width = min(80, max(20, w - 8))
            char_positions, total_rows = layout_text(target_text, max_width)
            continue

        if ch in (curses.KEY_BACKSPACE, 8, 127):
            if len(current_text) > 0:
                current_text.pop()
        elif 32 <= ch <= 126 and len(current_text) < len(target_text):
            if start_time is None:
                start_time = time.time()

            typed_char = chr(ch)
            expected_char = target_text[len(current_text)]
            if typed_char != expected_char:
                errors += 1
                # Track the stumbled character!
                errors_by_char[expected_char] = errors_by_char.get(expected_char, 0) + 1

            total_keystrokes += 1
            current_text.append(typed_char)


def main(stdscr):
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Correct character
    curses.init_pair(2, curses.COLOR_RED, -1)     # Incorrect character / alerts
    curses.init_pair(3, curses.COLOR_CYAN, -1)    # Title & highlights
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # Target text & general UI
    curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Selected / Stats / PBs
    curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Demo mode badge

    # Step 0: Welcome / Auth screen (Login, Create User, Demo)
    if not auth_screen(stdscr):
        return  # User pressed ESC to quit

    diff_choice = None
    length_choice = None

    while True:
        # Step 1: Select Difficulty or Stats or Switch User
        if diff_choice is None:
            diff_choice = difficulty_menu(stdscr)
            if diff_choice is None:
                break  # Exit
            if diff_choice == "stats":
                stats_dashboard(stdscr)
                diff_choice = None
                continue
            if diff_choice == "switch_user":
                if not auth_screen(stdscr):
                    break
                diff_choice = None
                continue

        # Step 2: Select Length
        if length_choice is None:
            length_choice = length_menu(stdscr, diff_choice)
            if length_choice is None:
                diff_choice = None  # Go back to difficulty selection
                continue

        # Run typing test
        action = run_test(stdscr, diff_choice, length_choice)

        if action == "quit":
            break
        elif action == "menu":
            length_choice = None  # Return to length menu (or ESC to go back to difficulty)
        elif action == "again":
            continue


def cli():
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--stats", "-s", "stats"):
        target = sys.argv[2] if len(sys.argv) > 2 else None
        stats_manager.print_cli_stats(target)
        return

    try:
        wrapper(main)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
